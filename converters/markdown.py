import textwrap
import pickle
import re
import string

def process_body(doc_pickle_file, output_file):
    document_body = None

    with open(doc_pickle_file, 'rb') as body_pickle:
        document_body = pickle.load(body_pickle)
        with open(output_file, 'w') as output:
            MarkdownConverter(document_body, output)

def process_body_raw(document_body, output_file):
    with open(output_file, 'w') as output:
        MarkdownConverter(document_body, output)


class MarkdownConverter():

    p_wrap = textwrap.TextWrapper(width = 70, break_long_words = False, break_on_hyphens = False)
    after_paragraph = []

    def __init__(self, document_body, body_md):
        try: 
            for k in document_body['content']:
                if 'paragraph' in k:
                    self.process_paragraph(k['paragraph'], body_md)
                elif 'sectionBreak' in k:
                    # ignore
                    pass
                else:
                    print(k)
        except BreakProcessing:
            print("Break processing for scratch section")
            return

        # body_md.write("\n<script async src=\"https://platform.twitter.com/widgets.js\" charset=\"utf-8\"></script>\n")

    def process_paragraph(self, para, body_md):
        if para['paragraphStyle']['namedStyleType'].startswith("HEADING_"):
            headingTags = {
                'HEADING_1': '#',
                'HEADING_2': '##',
                'HEADING_3': '###',
                'HEADING_4': '####'
            }

            tag = headingTags[para['paragraphStyle']['namedStyleType']]

            content = self.process_elements(para['elements']).strip()

            body_md.write("\n%s %s\n" % (tag, content))

        elif para['paragraphStyle']['namedStyleType'] == "NORMAL_TEXT":
            content = self.process_elements(para['elements'])

            prefix = ""
            if 'bullet' in para:
                prefix = "- "

            if content != "":
                body_md.write("%s%s" % (prefix, content))

            for a in self.after_paragraph:
                body_md.write(a + "\n")
            self.after_paragraph = []

        elif para['paragraphStyle']['namedStyleType'] == "TITLE":
            # ignore
            pass
        else:
            print(para['paragraphStyle'])

        # print(para)

    def process_elements(self, elements):

        content = ""

        for e in elements:            
            if 'textRun' in e:
                el_content = e['textRun']['content']

                if e['textRun']['textStyle'] != {}:
                    # if e['textRun']['textStyle'].get('baselineOffset') == 'SUBSCRIPT':
                    #     el_content = "\\textsubscript{%s}" % (el_content)
                    # elif 'link' in e['textRun']['textStyle']:
                    #     link = e['textRun']['textStyle']['link']['url']
                    #     el_content = "[%s](%s)" % (el_content, link)
                    # elif 'backgroundColor' in e['textRun']['textStyle'] and e['textRun']['textStyle']['backgroundColor']['color']['rgbColor'] == tweet_color:

                    #     tweet_text = el_content
                    #     tweet_text = tweet_text[0].upper() + tweet_text[1:]

                    #     if len(tweet_text) > 237:
                    #         print("Tweet too long (by %s): %s" % (len(tweet_text) - 237, tweet_text))

                    #     link = ("<a href=\"https://twitter.com/share?ref_src=twsrc%5Etfw\" " +
                    #               "class=\"twitter-share-button\" " +
                    #               "data-text=\"&ldquo;%s&rdquo;&#010;&#010;\" " % (tweet_text) +
                    #               "data-via=\"mseebach\" " +
                    #               "data-dnt=\"true\" " +
                    #               "data-show-count=\"false\">Tweet</a>")

                    #     tweet_link = ""
                    #     for l in self.p_wrap.wrap(tweet_text):
                    #         tweet_link += "> %s \n" % (l)

                    #     tweet_link += "> &nbsp;&nbsp;&nbsp; %s\n" % (link)

                    #     self.after_paragraph.append(tweet_link)
                    # elif 'backgroundColor' in e['textRun']['textStyle']:
                    #     pass
                    if 'italic' in e['textRun']['textStyle']:
                        el_content = "_%s_" % (el_content)
                    elif 'link' in e['textRun']['textStyle']:
                        link = e['textRun']['textStyle']['link']['url']
                        el_content = "[%s](%s)" % (el_content, link)
                    else:
                        print("TEXT STYLE:", e['textRun']['textStyle'])

                content += el_content

            elif 'horizontalRule' in e:
                content += "------\n"

        content = content.strip()
        if content == "":
            return "\n";

        if content == "===scratch":
            raise BreakProcessing()

        ## exclude content in {{..}} tags
        content = re.sub("{{.*}}", "", content)

        macro = re.search("\[macro:([a-z]+)(.*)\](.*)\[/macro\]", content)

        out = ""
        if macro:
            macro_name = macro.group(1)
            macro_content = getattr(self, "macro_" + macro_name)(macro.groups())
            out = content.replace(macro.group(0), macro_content)
        else:
            out = "\n".join(self.p_wrap.wrap(content))
            # for l in self.p_wrap.wrap(content):
            #     out += l + "\n"

        return out + "\n"


    def macro_tweet(self, groups):

        link = groups[1].strip()
        content = groups[2].strip()

        out = ""
        for l in self.p_wrap.wrap(content):
            out += "> %s\n" % (l)

        out += "> [↪](%s)\n" % (link)

        return out

    def macro_img(self, groups):
        img_path = groups[1].strip()
        caption = groups[2].strip()

        img_tag = """{%% include figure.html
              path="%s"
              class="img-fluid z-depth-1 rounded"
              alt="%s"
              caption="%s" %%}
              """ % (img_path, caption, caption)

        return img_tag


class BreakProcessing(Exception):
    pass
