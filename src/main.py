from functions import copy_content, generate_page, generate_pages_recursively
from htmlnode import LeafNode
from textnode import TextNode, TextType

def main():
    # node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    # node = TextNode("tae", TextType.LINK)
    copy_content("static", "public")
    # generate_page("content/index.md", "template.html", "public/index.html")
    # generate_page("content/blog/glorfindel/index.md", "template.html", "public/blog/glorfindel/index.html")
    # generate_page("content/blog/tom/index.md", "template.html", "public/tom/blog/index.html")
    # generate_page("content/blog/majesty/index.md", "template.html", "public/majesty/blog/index.html")
    # generate_page("content/contact/index.md", "template.html", "public/contact/index.html")
    generate_pages_recursively("content", "template.html", "public")

    
    


    


main()
