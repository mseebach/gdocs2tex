import textwrap
import pickle

def process_body(doc_pickle_file, output_file):
    document_body = None

    with open(doc_pickle_file, 'rb') as body_pickle:
        document_body = pickle.load(body_pickle)

    with open(output_file, 'w') as body_tex:
        for k in document_body['content']:
            if 'paragraph' in k:
                process_paragraph(k['paragraph'], body_tex)
            elif 'sectionBreak' in k:
                # ignore
                pass
            else:
                print(k)

p_wrap = textwrap.TextWrapper(width = 70, break_long_words = False, break_on_hyphens = False)

def process_paragraph(para, body_tex):
    if para['paragraphStyle']['namedStyleType'].startswith("HEADING_"):
        headingTags = {
            'HEADING_1': 'title',
            'HEADING_2': 'section',
            'HEADING_3': 'subsection',
            'HEADING_4': 'subsubsection'
        }

        tag = headingTags[para['paragraphStyle']['namedStyleType']]

        content = process_elements(para['elements'])

        latex_out = "\\%s*{%s}\n" % (tag, content)
        body_tex.write(latex_out)

    elif 'indentStart' in para['paragraphStyle']:
        # ignore
        pass
    elif para['paragraphStyle']['namedStyleType'] == "NORMAL_TEXT":
        content = process_elements(para['elements'])
        if content != "":
            for l in p_wrap.wrap(content):
                body_tex.write(l + "\n")
            body_tex.write("\n")

    elif para['paragraphStyle']['namedStyleType'] == "TITLE":
        # ignore
        pass
    else:
        print(para['paragraphStyle'])
    #print(para)

def process_elements(elements):

    char_replace = {
        u'\u2019': '\'',
        u'\u201c': '``',
        u'\u201d': '\'\'',
        u'\u2014': '---',
        u'$': '\\$',
    }

    content = ""

    for e in elements:
        el_content = e['textRun']['content']

        for (f, t) in char_replace.items():
            el_content = el_content.replace(f, t)

        if e['textRun']['textStyle'] != {}:
            if e['textRun']['textStyle'].get('baselineOffset') == 'SUBSCRIPT':
                el_content = "\\textsubscript{%s}" % (el_content)
            elif 'backgroundColor' in e['textRun']['textStyle']:
                # ignore test highlight
                pass
            else:
                print("TEXT STYLE:", e['textRun']['textStyle'])


        content += el_content

    return content.strip()
