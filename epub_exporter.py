# -*- coding: utf-8 -*-
from ebooklib import epub
import os
from bs4 import BeautifulSoup


class Ebook:
    def __init__(self):
        self._chapters = list()
        self.source_url = ""

    def init(self, title, cover):
        self.title = title
        self.cover = cover

    def get_last_chapter_title(self):
        return self._chapters[-1].title

    def load_from_file(self, path):
        loaded_epub= epub.read_epub(path)

        self.source_url = loaded_epub.get_metadata("wuxiadownloader","downloadurl")[0][0]

        self.title = loaded_epub.title

        epub_cover = get_items_of_type(epub.EpubCover, loaded_epub.items)[0]
        self.cover = epub_cover.content

        EpubHtmls = get_items_of_type(epub.EpubHtml, loaded_epub.get_items())
        for raw_chapter in EpubHtmls[1:]:
            title, text = parse_from_file(raw_chapter.content)
            chapter = epub.EpubHtml(title=title, file_name=title.lower().replace(" ", "-") + '.xhtml', lang='en')

            chapter.content = u'<h1>' + title + '</h1>' + text

            self._chapters.append(chapter)

    def save(self, path):
        if os.path.isfile(path):
            os.remove(path)
            
        book_content = epub.EpubBook()
        book_content = self.set_meta(book_content)

        # write to the file
        epub.write_epub(path, book_content, {})

    def status(self):
        return "You have " + str(len(self._chapters)) + " chapters loaded."

    def add_chapter(self, title, text):
        chapter = epub.EpubHtml(title=title, file_name=title.lower().replace(" ", "-")+ '.xhtml', lang='en')

        chapter.content = u'<h1>' + title + '</h1>'+text

        self._chapters.append(chapter)

    def update_chapters(self, update_list):
        update_list = update_list[::-1]
        for title, text in update_list:
            self.add_chapter(title, text)

    def set_meta(self, book_content):
        book_content.set_identifier(self.title.lower().replace(" ", "-"))
        book_content.set_title(self.title)
        book_content.set_language('en')
        book_content.set_cover("image.png", self.cover)

        for chapter in self._chapters:
            book_content.add_item(chapter)

        book_content.toc = self._chapters

        # add default NCX and Nav file
        book_content.add_item(epub.EpubNcx())
        book_content.add_item(epub.EpubNav())

        # define CSS style
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

        # add CSS file
        book_content.add_item(nav_css)

        # basic spine
        book_content.spine = ['nav', *self._chapters]

        book_content.set_unique_metadata("wuxiadownloader", "downloadurl", self.source_url)
        return book_content


def parse_from_file(raw):
    soup = BeautifulSoup(raw, "lxml")
    title = soup.find("title").get_text()

    content = list()
    for p in soup.find_all('p')[1:]:
        if len(p.text) > 0:
            content.append(str(p))
    content = ''.join(content)
    return title, content


def get_items_of_type(typ, containter):
    ret_list = list()

    for item in containter:
        if type(item) is typ:
            ret_list.append(item)
    return ret_list
