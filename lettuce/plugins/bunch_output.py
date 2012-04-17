from datetime import datetime
from lettuce.terrain import after
from lettuce.terrain import before
from xml.dom import minidom
from functools import wraps
from types import StringTypes, BooleanType, IntType, \
    LongType, FloatType, ComplexType, \
    DictType, ListType, TupleType


NonStringElementaryTypes = (BooleanType, IntType, LongType, FloatType, ComplexType)
SimpleTypes = StringTypes + NonStringElementaryTypes
SequenceTypes = (ListType, TupleType)
DictTypes = (DictType,)
ContainerTypes = SequenceTypes + DictTypes
AllowedTypes = ContainerTypes + SimpleTypes

try:
    import lxml.etree as ET
except ImportError:
    try:
        import cElementTree as ET
    except ImportError:
        import xml.etree.ElementTree as ET

class PluginState(object):
    def __init__(self, **kw):
        self.set_atts = kw
        for arg in kw:
            setattr(self, arg, kw[arg])

    def clear(self):
        for attr in self.set_atts:
            setattr(self, attr, self.set_atts[attr])
            
    def set(self, name, value):
        setattr(self, name, value)
    
    def get(self, name):
        return getattr(self, name)

BUNCH_PLUGIN = PluginState(
    enabled=False,
    filename=None,

    features=None,
    feature=None,
    feature_started=None,
    feature_finished=None,

    scenarios=None,
    scenario=None,
    scenario_started=None,
    scenario_finished=None,

    steps=None,
    step=None,
    step_started=None,
    step_finished=None,

    outlines=None,
    outline=None,
    outline_started=None,
    outline_finished=None
)

def enable(filename):
    BUNCH_PLUGIN.enabled = True
    BUNCH_PLUGIN.filename = filename

def disable():
    BUNCH_PLUGIN.clear()

def write_output(filename, element):
    ET.ElementTree(element).write(filename, encoding='utf-8',xml_declaration=True)

def switch(f):
    @wraps(f)
    def on_off(*args, **kwargs):
        if BUNCH_PLUGIN.enabled:
            return f(*args, **kwargs)

    return on_off

@before.all
@switch
def prepare():
    BUNCH_PLUGIN.features = ET.Element("features")

def update_compound_attr(element, name, value):
    if name == 'why' and value is not None:
        add_failure_reasons([value], element)
    elif isinstance(value, ContainerTypes) and len(value) > 0:
        xml_serialize_container(element, name, value)


def filter_item_attributes(attr, excluded=set(['original_string'])):
    if attr.startswith("_") or attr in excluded:
        return False

    return True

def getSubElement(element, name, allow_duplicates=False):
    sub = element.find(name)
    if not allow_duplicates and sub is not None:
        return sub
    return ET.SubElement(element, name)

def createDictItem(dict_element, key):
    new_item = ET.SubElement(dict_element, 'item')
    new_key = ET.SubElement(new_item, 'key')
    new_key.text = key
    new_value = ET.SubElement(new_item, 'value')
    return new_key, new_value

def getDictElement(dict_element, key):
    for item in dict_element.iterfind('item'):
        key_element = getSubElement(item, 'key')
        if key_element.text == key:
            return key_element, getSubElement(item, 'value')

    return createDictItem(dict_element, key)

def createSeqElement(seq_element, index):
    new_item = ET.SubElement(seq_element, 'item')
    new_item.set('id', str(index))
    return new_item

def getSeqElement(seq_element, index):
    elem =  seq_element.find("item[@id='%s']" % index)
    if elem is not None:
        return elem

    return createSeqElement(seq_element, index)

def setTypeAttribute(element, value):
    element.set('type', type(value).__name__)

def xml_serialize_container(parent_element, name, s):
    if isinstance(s, SequenceTypes):
        xml_serialize_seq(parent_element, name, s)
    elif isinstance(s, DictTypes):
        xml_serialize_dict(parent_element, name, s)

def xml_serialize_seq(parent_element, name, s):
    filtered_seq = filter(lambda x: isinstance(x, AllowedTypes), s)
    if len(filtered_seq) > 0:
        seq_xml_root = getSubElement(parent_element, name)
        setTypeAttribute(seq_xml_root,s)
        i = 0
        for item in filtered_seq:
            item_xml = getSeqElement(seq_xml_root, i)
            setTypeAttribute(item_xml, item)
            i += 1
            if isinstance(item, SimpleTypes):
                item_xml.text = str(item)
            elif isinstance(item, ContainerTypes):
                xml_serialize_container(item_xml, "itemvalue", item)

def xml_serialize_dict(parent_element, name, d):
    dict_element = getSubElement(parent_element, name)
    setTypeAttribute(dict_element,d)
    for key, value in d.iteritems():
        key_element,value_element = getDictElement(dict_element, key)
        key_element.text = key
        setTypeAttribute(value_element, value)
        if isinstance(value, SimpleTypes):
            value_element.text = str(value)
        elif isinstance(value, DictType):
            xml_serialize_container(value_element, key, value)


def xml_serialize_primitive(parent_element, name, value):
    sub = getSubElement(parent_element,name)
    sub.text = str(value)
    setTypeAttribute(sub, value)

def update_attributes_of_xml_element(element, obj, allow_duplicates=False):
    props = getSubElement(element, 'properties')
    for attr in filter(filter_item_attributes, dir(obj)):
        if isinstance(getattr(obj, attr), SimpleTypes):
            xml_serialize_primitive(props, attr, getattr(obj, attr))
        else:
            update_compound_attr(props, attr, getattr(obj, attr))

def add_timing(element, dt, timing_tag):
    timing = ET.SubElement(element, timing_tag)
    timing.text = dt.isoformat()

def add_started(element, dt):
    add_timing(element, dt, 'started')

def add_finished(element, dt):
    add_timing(element, dt, 'finished')

def add_results(element, passed=None, delta=None):
    if delta is not None:
        ET.SubElement(element, 'time').text = "%f" % (delta.total_seconds())

    result = ET.SubElement(element, 'result')
    if passed is None:
        result.text = 'skipped'
    elif passed:
        result.text = 'passed'
    else:
        result.text = 'failed'

def add_item(item, root_elem, elem, allow_duplicates=False):
    BUNCH_PLUGIN.set(
        elem,
        ET.SubElement(
            BUNCH_PLUGIN.get(root_elem),
            elem))
    update_attributes_of_xml_element(BUNCH_PLUGIN.get(elem), item, allow_duplicates)
    started = datetime.now()
    BUNCH_PLUGIN.set( elem + '_started', started)
    add_started(BUNCH_PLUGIN.get(elem), started)

def add_item_results(item, elem, success=None):
    finished = datetime.now()
    update_attributes_of_xml_element(BUNCH_PLUGIN.get(elem), item)
    BUNCH_PLUGIN.set( elem + '_finished', finished)
    elem_object = BUNCH_PLUGIN.get(elem)
    add_finished(elem_object, finished)
    started = BUNCH_PLUGIN.get(elem + '_started')
    add_results(elem_object, success, finished - started + datetime.resolution)

def add_failure_reason(failure_elem, reason):
    reason_elem = ET.SubElement(failure_elem, 'reason')
    ET.SubElement(reason_elem, 'cause').text = reason.cause
    ET.SubElement(reason_elem, 'traceback').text = reason.traceback

def add_failure_reasons(reasons, parent_elem):
    if len(reasons):
        failure_elem = getSubElement(parent_elem, "failure")
        for reason in reasons:
            add_failure_reason(failure_elem, reason)

def add_children(elem, children_root):
    BUNCH_PLUGIN.set(children_root,
        ET.SubElement(elem, children_root))

def decide_item_success(item):
    if not item.ran:
        return None

    return not item.failed

def decide_outline_success(reasons_to_fail):
    return len(reasons_to_fail) == 0

def decide_item_success_by_subitems(xml_item, subitems_name):
    if xml_item is not None:
        subs = xml_item.findall(subitems_name + '/result')
        if subs:
            for sub in subs:
                if sub.text == 'failed':
                    return False

            subs = filter(lambda x: x.text != 'skipped', subs)
            if not len(subs):
                return None

    return True

@before.each_feature
@switch
def add_feature(feature):
    """add_feature"""
    add_item(feature, 'features', 'feature')
    add_children(BUNCH_PLUGIN.feature, 'scenarios')

@after.each_feature
@switch
def add_feature_results(feature):
    """add_feature_results"""
    add_item_results(feature, 'feature', decide_item_success_by_subitems(BUNCH_PLUGIN.scenarios, 'scenario'))

@before.each_scenario
@switch
def add_scenario(scenario):
    """add_scenario"""
    add_item(scenario, 'scenarios', 'scenario')
    add_children(BUNCH_PLUGIN.scenario, 'steps')
    add_children(BUNCH_PLUGIN.scenario, 'outlines')

@after.each_scenario
@switch
def add_scenario_results(scenario):
    """add_scenario_results"""
    add_item_results(scenario, 'scenario',
        decide_item_success_by_subitems(BUNCH_PLUGIN.steps, 'step')
        and
        decide_item_success_by_subitems(BUNCH_PLUGIN.outlines, 'outline'))

@before.each_step
@switch
def add_step(step):
    add_item(step, 'steps', 'step')


@after.each_step
@switch
def add_step_results(step):
        add_item_results(step, 'step', decide_item_success(step))

@before.outline
@switch
def add_outline(scenario, order, outline, reasons_to_fail):
    """add_outline"""
    add_item(outline, 'outlines', 'outline')

@after.outline
@switch
def add_outline_results(scenario, order, outline, reasons_to_fail):
    """add_outline_results"""
    add_item_results(outline, 'outline', decide_outline_success(reasons_to_fail))
    add_failure_reasons(reasons_to_fail, BUNCH_PLUGIN.get('outline'))


@after.all
@switch
def output_xml(total):
    write_output(BUNCH_PLUGIN.filename, BUNCH_PLUGIN.features)



