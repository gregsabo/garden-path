from lxml import etree


def parse_xml(xml):
    """
    xml string -> etree element, according to my preferences.
    """
    return etree.fromstring(xml, etree.XMLParser(remove_blank_text=True))


def encode_xml(xml):
    """
    etree element -> xml string, pretty printed.
    """
    return etree.tostring(xml, pretty_print=True).decode("utf-8")