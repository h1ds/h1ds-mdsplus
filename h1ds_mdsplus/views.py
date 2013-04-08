import re, json, StringIO, csv
import pylab
import xml.etree.ElementTree as etree

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404, StreamingHttpResponse
from django.contrib import messages
from django.conf import settings
from django.core.cache import cache
from django.views.generic import View, RedirectView

from MDSplus import Tree
from MDSplus._treeshr import TreeException

from h1ds_mdsplus.utils import url_path_components_to_mds_path
from h1ds_mdsplus.wrappers import NodeWrapper
import h1ds_mdsplus.filters as df
from h1ds_mdsplus.utils import new_shot_generator

from h1ds_core.views import get_filter_list
from h1ds_core.models import UserSignal, UserSignalForm

DEFAULT_TAGNAME = "top"
DEFAULT_NODEPATH = ""

########################################################################
## Helper functions                                                   ##
########################################################################

# Match any URL path component comprising only digits.
# e.g. "foo/bar/12345/stuff" -> 12345
shot_regex = re.compile(r".*?\/(\d+?)\/.*?")

def get_subtree(mds_node):

    try:
        desc = map(get_subtree, mds_node.getDescendants())
    except TypeError:
        desc = []

        tree = {
        "id":unicode(mds_node.nid),
        "name":unicode(mds_node.getNodeName()),
        "data":{"$dim":0.5*len(desc)+1, "$area":0.5*len(desc)+1, "$color":"#888"},
        "children":desc,
        }
    return tree

def get_nav_for_shot(tree, shot):
    mds_tree = Tree(tree, shot, 'READONLY')
    root_node = mds_tree.getNode(0)
    return get_subtree(root_node)
    
####def get_tree_exception_response()


########################################################################
## Django views                                                       ##
########################################################################


class NodeMixin(object):
    def get_node(self):
        tagname = self.kwargs.get('tagname', DEFAULT_TAGNAME)
        nodepath = self.kwargs.get('nodepath', DEFAULT_NODEPATH)
        try:
            mds_tree = Tree(self.kwargs['tree'], int(self.kwargs['shot']), 'READONLY')
        except TreeException:
            # If the  data cannot be  found, raise HTTP 404  error. HTTP
            # 404 is  appropriate, as  the requested resource  cannot be
            # found,  but may be  available in  the future  (i.e. future
            # shot number)
            raise Http404
        mds_path = url_path_components_to_mds_path(self.kwargs['tree'], tagname, nodepath)
        return NodeWrapper(mds_tree.getNode(mds_path))

    def get_filtered_node(self, request):
        mds_node = self.get_node()
        
        for fid, name, args, kwargs in get_filter_list(request):
            #if u'' in args:
            #    messages.info(request, "Error: Filter '%s' is missing argument(s)" %(name))
            #    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            mds_node.data.apply_filter(fid, name, *args, **kwargs)
        return mds_node

class JSONNodeResponseMixin(NodeMixin):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        mds_node = self.get_filtered_node(request)
        data_dict = mds_node.get_view('json', dict_only=True)
        html_metadata = {
            'mds_path':unicode(mds_node.mds_object.getFullPath()),
            'mds_tree':mds_node.mds_object.tree.name,
            'mds_shot':mds_node.mds_object.tree.shot,
            'mds_node_id':mds_node.mds_object.nid,
            }
        # add metadata...
        data_dict.update({'meta':html_metadata})
        return HttpResponse(json.dumps(data_dict), mimetype='application/json')

class CSVNodeResponseMixin(NodeMixin):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        mds_node = self.get_filtered_node(request)
        data = mds_node.get_view('csv')
        
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=data.csv'

        writer = csv.writer(response)
        for i in data:
            writer.writerow(map(str, i))
        return response


class XMLNodeResponseMixin(NodeMixin):
    """TODO: Generalise this for all datatypes"""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        mds_node = self.get_filtered_node(request)
        # TODO: this should be handled by wrappers
        # however, at present mds_node.get_view
        # calls get_view on the data object which
        # doesn't ?? know about shot info, etc
        # the proper fix might be to have wrappers
        # take as args wrappers rather than data objects?
        
        data_xml = etree.Element('{http://h1svr.anu.edu.au/mdsplus}mdsdata',
                                 attrib={'{http://www.w3.org/XML/1998/namespace}lang': 'en'})

        # add shot info
        shot_number = etree.SubElement(data_xml, 'shot_number', attrib={})
        shot_number.text = str(mds_node.mds_object.tree.shot)
        shot_time = etree.SubElement(data_xml, 'shot_time', attrib={})
        shot_time.text = str(mds_node.mds_object.getTimeInserted().date)
        

        # add mds info
        mds_tree = etree.SubElement(data_xml, 'mds_tree', attrib={})
        mds_tree.text = mds_node.mds_object.tree.name
        mds_path = etree.SubElement(data_xml, 'mds_path', attrib={})
        mds_path.text = repr(mds_node.mds_object)

        signal = etree.SubElement(data_xml, 'data', attrib={'type':'signal'})

        ## make xlink ? to signal binary 
        ## for now, just text link
        #### should use proper url joining rather than string hacking...
        signal.text = request.build_absolute_uri()
        if '?' in signal.text:
            # it doesn't matter if we have multiple 'view' get queries - only the last one is used
            signal.text += '&view=bin' 
        else:
            signal.text += '?view=bin'

        return HttpResponse(etree.tostring(data_xml), mimetype='text/xml; charset=utf-8')

class PNGNodeResponseMixin(NodeMixin):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        mds_node = self.get_filtered_node(request)
        data = mds_node.get_view('png')
        img_buffer = StringIO.StringIO()
        pylab.imsave(img_buffer, data.data, format='png')
        return HttpResponse(img_buffer.getvalue(), mimetype='image/png')

class BinaryNodeResponseMixin(NodeMixin):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        mds_node = self.get_filtered_node(request)
        disc_data = mds_node.get_view('bin')
        response = HttpResponse(disc_data['iarr'].tostring(), mimetype='application/octet-stream')
        response['X-H1DS-signal-min'] = disc_data['minarr']
        response['X-H1DS-signal-delta'] = disc_data['deltar']
        response['X-H1DS-dim-t0'] = mds_node.data.dim[0]
        response['X-H1DS-dim-delta'] = mds_node.data.dim[1]-mds_node.data.dim[0]
        response['X-H1DS-dim-length'] = len(mds_node.data.dim)
        response['X-H1DS-signal-units'] = mds_node.data.units
        response['X-H1DS-signal-dtype'] = str(disc_data['iarr'].dtype)
        response['X-H1DS-dim-units'] = mds_node.data.dim_units
        return response

    
class HTMLNodeResponseMixin(NodeMixin):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        mds_node = self.get_filtered_node(request)

        # get any saved signals for the user
        if request.user.is_authenticated():
            user_signals = UserSignal.objects.filter(user=request.user)
            user_signal_form = UserSignalForm()
        else:
            user_signals = []
            user_signal_form = None            
        html_metadata = {
            'mds_tree':mds_node.mds_object.tree.name,
            'mds_shot':mds_node.mds_object.tree.shot, 
            'mds_node_id':mds_node.mds_object.nid,
            #'user_signals':user_signals,
            #'node_display_info':mds_node.get_display_info(),
            }

        return render_to_response('h1ds_mdsplus/node.html', 
                                  {'node_content':mds_node.get_view('html'),
                                   'html_metadata':html_metadata,
                                   'user_signals':user_signals,
                                   'user_signal_form':user_signal_form,
                                   'mdsnode':mds_node,
                                   'request_fullpath':request.get_full_path()},
                                  context_instance=RequestContext(request))

class MultiNodeResponseMixin(HTMLNodeResponseMixin, JSONNodeResponseMixin, PNGNodeResponseMixin, XMLNodeResponseMixin, BinaryNodeResponseMixin, CSVNodeResponseMixin):
    """Dispatch to requested representation."""

    representations = {
        "html":HTMLNodeResponseMixin,
        "json":JSONNodeResponseMixin,
        "png":PNGNodeResponseMixin,
        "xml":XMLNodeResponseMixin,
        "bin":BinaryNodeResponseMixin,
        "csv":CSVNodeResponseMixin,
        }

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method for requested representation; 
        # if a method doesn't exist, defer to the error handler. 
        # Also defer to the error handler if the request method isn't on the approved list.
        
        # TODO: for now, we only support GET and POST, as we are using the query string to 
        # determing which representation should be used, and the querydict is only available
        # for GET and POST. Need to bone up on whether query strings even make sense on other
        # HTTP verbs. Probably, we should use HTTP headers to figure out which content type should be
        # returned - also, we might be able to support both URI and header based content type selection.
        # http://stackoverflow.com/questions/381568/rest-content-type-should-it-be-based-on-extension-or-accept-header
        # http://www.xml.com/pub/a/2004/08/11/rest.html

        if request.method == 'GET':
            requested_representation = request.GET.get('view', 'html').lower()
        elif request.method == 'POST':
            requested_representation = request.GET.get('view', 'html')
        else:
            # until we figure out how to determine appropriate content type
            return self.http_method_not_allowed(request, *args, **kwargs)

        if not requested_representation in self.representations:
            # TODO: should handle this and let user know? rather than ignore?
            requested_representation = 'html'
            
        rep_class = self.representations[requested_representation]

        if request.method.lower() in rep_class.http_method_names:
            handler = getattr(rep_class, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return handler(self, request, *args, **kwargs)


class NodeView(MultiNodeResponseMixin, View):
    pass

class TreeOverviewView(RedirectView):   
    # TODO: currently HTML only.
    http_method_names = ['get']
    def get_redirect_url(self, **kwargs):
        return reverse('mds-root-node', kwargs={'tree':kwargs['tree'], 'shot':0})


class HomepageView(RedirectView):    

    def get_redirect_url(self, **kwargs):
        return reverse('mds-tree-overview', args=[settings.DEFAULT_TREE])

