import unittest
from functions import BlockType, block_to_block_type, extract_markdown_images, extract_markdown_links, extract_title, generate_page, markdown_to_blocks, markdown_to_html_node, split_nodes_delimiter, split_nodes_image, split_nodes_link, text_to_textnodes
from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextType, text_node_to_html_node

class TestInlineMarkdown(unittest.TestCase):
    def test_to_html_props(self):
        node = HTMLNode(
            "div",
            "Hello, world",
            None,
            {"class": "greeting", "href":"https://boot.dev"}
        )
        self.assertEqual(
            node.props_to_html(),
            ' class="greeting" href="https://boot.dev"'
        )

    def test_values(self):
        node = HTMLNode(
            "div",
            "I wish I could read",
        )

        self.assertEqual(
            node.tag,
            "div"
        )

        self.assertEqual(
            node.value,
            "I wish I could read"
        )

        self.assertEqual(
            node.children,
            None
        )

        self.assertEqual(
            node.props,
            None
        )

    def test_repr(self):
        node = HTMLNode(
            "p",
            "What a strange world",
            None,
            {"class": "primary"},
        )
        self.assertEqual(
            node.__repr__(),
            "HTMLNode(p, What a strange world, children: None, {'class': 'primary'})",
        )

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_div(self):
        node = LeafNode("div", "Shet")
        self.assertEqual(node.to_html(), "<div>Shet</div>")

    def test_leaf_to_html_link(self):
        node = LeafNode("a", "Link to boot dev", {"href": "https://boot.dev"})
        self.assertEqual(node.to_html(), '<a href="https://boot.dev">Link to boot dev</a>')

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_grandchildren_with_values(self):
        grandchild_node = LeafNode("b", "grandchild", {"href": "#"})
        child_node = ParentNode("span", [grandchild_node], {"class": "primary"})
        parent_node = ParentNode("div", [child_node], {"style": "margin-top: 50px"})
        self.assertEqual(
            parent_node.to_html(),
            '<div style="margin-top: 50px"><span class="primary"><b href="#">grandchild</b></span></div>',
        )

    def test_extract_markdown_images(self):
        text = [
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
                ]

        expected = [
            [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")],
            [("image", "https://i.imgur.com/zjjcJKZ.png")]
                    ]
        
        for i in range(len(text)):
            result = extract_markdown_images(text[i])
            self.assertEqual(result, expected[i])

    def test_extract_markdown_links(self):
        text = [
            "This is text with a [rick roll](https://i.imgur.com/aKaOqIh.gif) and [obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
            "This is text with an [image](https://i.imgur.com/zjjcJKZ.png)"
                ]

        expected = [
            [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")],
            [("image", "https://i.imgur.com/zjjcJKZ.png")]
                    ]
        
        for i in range(len(text)):
            result = extract_markdown_links(text[i])
            self.assertEqual(result, expected[i])

    def test_split(self):
        node = TextNode("This is text with a `code block`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block",  TextType.CODE),
        ]

        self.assertEqual(new_nodes,expected) 

    def test_split_multiple(self):
        node_first = TextNode("This is text with a **bold** word", TextType.TEXT)
        node_second = TextNode(str("Second **bold** word"), TextType.TEXT)

        new_nodes = split_nodes_delimiter([node_first, node_second], "**", TextType.BOLD)

        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bold",  TextType.BOLD),
            TextNode(" word", TextType.TEXT),
            TextNode("Second ", TextType.TEXT),
            TextNode("bold",  TextType.BOLD),
            TextNode(" word", TextType.TEXT),
        ]

        self.assertEqual(new_nodes,expected) 

    def test_split_multiple_with_another_type(self):
        node_first = TextNode("This is text with a **bold** word", TextType.TEXT)
        node_second = TextNode(str("Second **bold** word"), TextType.TEXT)
        node_third = TextNode(str("THIS IS BOLD TEXT"), TextType.BOLD)
        node_fourth = TextNode(str("THIS IS ITALIC TEXT"), TextType.ITALIC)

        new_nodes = split_nodes_delimiter([node_first, node_second, node_third, node_fourth], "**", TextType.BOLD)

        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bold",  TextType.BOLD),
            TextNode(" word", TextType.TEXT),
            TextNode("Second ", TextType.TEXT),
            TextNode("bold",  TextType.BOLD),
            TextNode(" word", TextType.TEXT),
            TextNode("THIS IS BOLD TEXT", TextType.BOLD),
            TextNode("THIS IS ITALIC TEXT", TextType.ITALIC),

        ]

        self.assertEqual(new_nodes,expected) 

    def test_delim_bold(self):
        node = TextNode("This is text with a **bolded** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delim_bold_double(self):
        node = TextNode(
            "This is text with a **bolded** word and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_bold_multiword(self):
        node = TextNode(
            "This is text with a **bolded word** and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded word", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_italic(self):
        node = TextNode("This is text with an _italic_ word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delim_bold_and_italic(self):
        node = TextNode("**bold** and _italic_", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
            new_nodes,
        )

    def test_delim_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT
        )
        expectation = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
        ]

        self.assertEqual(split_nodes_image([node]), expectation)

        #With trail
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png) this is the trailing part",
            TextType.TEXT
        )
        expectation = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            TextNode(" this is the trailing part", TextType.TEXT),
        ]

        self.assertEqual(split_nodes_image([node]), expectation)

        #Multiple Nodes
        first_node = TextNode(
            "This is first dog ![first dog](https://unsplash.com/photos/a-golden-retriever-sitting-on-a-sandy-beach-FTbC150wV8Q)",
            TextType.TEXT
        )
        second_node = TextNode(
            "This is second dog ![second dog](https://unsplash.com/photos/yellow-labrador-retriever-biting-yellow-tulip-flower-Sg3XwuEpybU)",
            TextType.TEXT
        )
        third_node = TextNode(
            "This is third dog ![third dog](https://unsplash.com/photos/dog-running-on-beach-during-daytime-yihlaRCCvd4)",
            TextType.TEXT
        )

        expectation = [
            TextNode("This is first dog ", TextType.TEXT),
            TextNode("first dog", TextType.IMAGE, "https://unsplash.com/photos/a-golden-retriever-sitting-on-a-sandy-beach-FTbC150wV8Q"),
            TextNode("This is second dog ", TextType.TEXT),
            TextNode("second dog", TextType.IMAGE, "https://unsplash.com/photos/yellow-labrador-retriever-biting-yellow-tulip-flower-Sg3XwuEpybU"),
            TextNode("This is third dog ", TextType.TEXT),
            TextNode("third dog", TextType.IMAGE, "https://unsplash.com/photos/dog-running-on-beach-during-daytime-yihlaRCCvd4"),
        ]

        self.assertEqual(split_nodes_image([first_node, second_node, third_node]), expectation)

        expectation = []

        #Empty Node
        self.assertEqual(split_nodes_image([]), expectation)

        #BOots 
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_split_link(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )        

        expectation = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]

        self.assertEqual(split_nodes_link([node]), expectation)

    def test_split_image_single(self):
        node = TextNode(
            "![image](https://www.example.COM/IMAGE.PNG)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://www.example.COM/IMAGE.PNG"),
            ],
            new_nodes,
        )

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and [another link](https://wikipedia.org) with text that follows",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("another link", TextType.LINK, "https://wikipedia.org"),
                TextNode(" with text that follows", TextType.TEXT),
            ],
            new_nodes,
        )
    #Testing equal text types
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    #Testing inequality with different text types 
    def test_not_eq_text_type(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    #Testing inequality with different text content 
    def test_not_eq_text_content(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a different text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    #Testing inequality with different text content 
    def test_eq_url(self):
        node = TextNode("This is a text node", TextType.LINK, "https://www.boot.dev")
        node2 = TextNode("This is a text node", TextType.LINK, None)
        self.assertNotEqual(node, node2)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)

    def test_all(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertEqual(text_to_textnodes(text),
        [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_newlines(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_type(self):
        #Check if paragraph  
        text = "1.This is a paragraph"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(text))
        text = "1. This is a paragraph\n 3.This is also a paragraph in an ordered list like"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(text))

        #Check if heading
        text = "# This is a heading"
        self.assertEqual(BlockType.HEADING, block_to_block_type(text))
        #Check if heading has space
        text = "#This is a heading"
        self.assertNotEqual(BlockType.HEADING, block_to_block_type(text))

        #Check if code
        text = "```\n This sample code ```" 
        self.assertEqual(BlockType.CODE, block_to_block_type(text))
        #Check if code ``` at the end has new line
        text = "```\n This sample code\n```" 
        self.assertEqual(BlockType.CODE, block_to_block_type(text))

        #Check if quote
        text = "> This is a quote"
        self.assertEqual(BlockType.QUOTE, block_to_block_type(text))

        #Check if quote no space
        text = ">This is a quote"
        self.assertEqual(BlockType.QUOTE, block_to_block_type(text))

        #Check if unordered list 
        text = "- List 1\n - List 2"
        self.assertEqual(BlockType.UNORDERED_LIST, block_to_block_type(text))

        #Check if ordered list 
        text = "1. List 1\n 2. List 2"
        self.assertEqual(BlockType.ORDERED_LIST, block_to_block_type(text))
    def test_block_to_block_types(self):
        block = "# heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
        block = "```\ncode\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
        block = "> quote\n> more quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)
        block = "- list\n- items"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)
        block = "1. list\n2. items"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)
        block = "paragraph"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )


    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_paragraph(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p></div>",
        )

    def test_paragraphs_new(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_unordered_list(self):
        md="""
- This is first
- This is second
- This is third
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><ul><li>This is first</li><li>This is second</li><li>This is third</li></ul></div>")

    def test_lists(self):
        md = """
- This is a list
- with items
- and _more_ items

1. This is an `ordered` list
2. with items
3. and more items

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>This is a list</li><li>with items</li><li>and <i>more</i> items</li></ul><ol><li>This is an <code>ordered</code> list</li><li>with items</li><li>and more items</li></ol></div>",
        )

    def test_headings(self):
        md = """
# this is an h1

this is paragraph text

## this is an h2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>this is an h1</h1><p>this is paragraph text</p><h2>this is an h2</h2></div>",
        )

    def test_blockquote(self):
        md = """
> This is a
> blockquote block

this is paragraph text

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a blockquote block</blockquote><p>this is paragraph text</p></div>",
        )

    def test_code(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_get_header(self):
        md = """
```
# This is a sample markdown header
This is a sample markdown
```
"""
        get_header = extract_title(md)
        self.assertEqual(
            "This is a sample markdown header",
            get_header
        )

        no_header_md = """
```
This is a sample markdown file
This markdown does not heave a header
```
"""
        self.assertRaises(
            Exception,
            extract_title,
            no_header_md
        )



if __name__ == "__main__":
    unittest.main()

