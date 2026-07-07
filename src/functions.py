from enum import Enum
from os.path import exists, isfile
import re
from htmlnode import HTMLNode, ParentNode
from textnode import TextNode, TextType, text_node_to_html_node
import os
import shutil
import pathlib

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def split_nodes_delimiter(old_nodes: list[TextNode], delimeter: str, text_type: TextType) -> list[TextNode]:
    new_nodes = [] 

    for old_node in old_nodes:
        if old_node.text_type !=TextType.TEXT:
            new_nodes.append(old_node)
            continue

        split_nodes = []
        sections = old_node.text.split(delimeter)

        if len(sections) % 2 == 0:
            raise ValueError("Invalid markdown, formatted section not closed")

        for i in range(len(sections)):
            if sections[i] == "":
                continue

            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        
        new_nodes.extend(split_nodes)
                
    return new_nodes

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)",text)

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)",text)

def split_nodes_image(old_nodes: list[TextNode])-> list[TextNode]:
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT and old_node.text:
            new_nodes.append(old_node)
            continue

        original_text = old_node.text
        extracted_images = extract_markdown_images(original_text)


        for extracted_image in extracted_images:
            image_alt =extracted_image[0] 
            image_link =extracted_image[1] 

            sections = original_text.split(f"![{image_alt}]({image_link})", 1)
            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))


            new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_link))
            original_text = sections[1]

        if len(original_text) > 0:
            new_nodes.append(TextNode(original_text, TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes: list[TextNode])-> list[TextNode]:
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        original_text = old_node.text
        extracted_images = extract_markdown_links(original_text)


        for extracted_image in extracted_images:
            link_text =extracted_image[0] 
            link_url =extracted_image[1] 

            sections = original_text.split(f"[{link_text}]({link_url})", 1)
            new_nodes.append(TextNode(sections[0], TextType.TEXT))

            new_nodes.append(TextNode(link_text, TextType.LINK, link_url))
            original_text = sections[1]

        if len(original_text) > 0:
            new_nodes.append(TextNode(original_text, TextType.TEXT))

    return new_nodes

def text_to_textnodes(text):
    node = TextNode(text, TextType.TEXT)

    node = split_nodes_delimiter([node], "**", TextType.BOLD)
    node = split_nodes_delimiter(node, "_", TextType.ITALIC)
    node = split_nodes_delimiter(node, "`", TextType.CODE)
    node = split_nodes_image(node)
    node = split_nodes_link(node)

    return node

def markdown_to_blocks(markdown):
    return [x for x in list(map(lambda x: x.strip(), markdown.split("\n\n"))) if x]

def block_to_block_type(text)->BlockType:
    new_text = text.split()
    if "#" in new_text[0]:
        hash_count = len(new_text[0]) 
        if new_text[0] == '#' * hash_count and hash_count > 0 and hash_count <= 6:
             return BlockType.HEADING
    if f"{text[0]}{text[1]}{text[2]}{text[3]}" == "```\n" and text[:3] == "```":
        return BlockType.CODE
    if f"{text[0]}" == ">":
        for line in text.split("\n"):
            if f"{line[0]}" == ">":
                continue
            else:
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    if f"{text[0]}{text[1]}" == "- ":
        for line in text.split("\n"):
            if f"{line[0]}{line[1]}" == "- ":
                return BlockType.UNORDERED_LIST
            else:
                return BlockType.PARAGRAPH
    if any(char.isdigit() for char in new_text[0]):
        ordered_list = text.split("\n")

        is_ordered_list = True
        for i in range(len(ordered_list)):
            tmp = ordered_list[i]
            tmp = tmp.strip()
            

            if f"{i+1}. " != f"{tmp[0]}{tmp[1]}{tmp[2]}":
                is_ordered_list = False

        if is_ordered_list:
            return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

#Helpers
def determine_tag(block_type:BlockType)->str:
    tag = None
    match(block_type):
        case BlockType.PARAGRAPH:
            tag = 'p'
        case BlockType.HEADING:
            tag = 'h1'
        case BlockType.CODE:
            tag = 'code'
        case BlockType.QUOTE:
            tag = 'blockquote'
        case BlockType.UNORDERED_LIST:
            tag = 'ul'
        case BlockType.ORDERED_LIST:
            tag = 'ol'
    return tag

def text_to_children(text):
    children = []

    result = text_to_textnodes(text)
    for res in result:
        children.append(text_node_to_html_node(res))

    return children

def get_block_nodes(markdown):
    block_nodes = []

    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.CODE:
            block = block[4:-3]
            tmp_node = [text_node_to_html_node(TextNode(text=block, text_type=TextType.CODE))]
            children = ParentNode(tag="pre", children=tmp_node)
            block_nodes.append(children)
        elif block_type == BlockType.QUOTE:
            lines = list(map(lambda x: x.lstrip(">").strip(), block.split("\n"))) 
            paragraph = " ".join(lines)
            children = text_to_children(paragraph)
            block_node = ParentNode(tag=determine_tag(block_type), children=children)
            block_nodes.append(block_node)
        elif block_type == BlockType.HEADING:
            lines = block.split() 
            hash_count = len(lines.pop(0))
            if hash_count <= 6:
                paragraph = " ".join(lines)
                children = text_to_children(paragraph)
                block_node = ParentNode(tag=f"h{hash_count}", children=children)
                block_nodes.append(block_node)
        elif block_type == BlockType.UNORDERED_LIST:
            lines = list(map(lambda x: x.lstrip('-').strip(), block.split("\n"))) 

            final_nodes = []
            for line in lines:
                children = text_to_children(line)
                final_nodes.append(ParentNode(tag="li", children=children))

            block_node = ParentNode(tag=determine_tag(block_type), children=final_nodes)
            block_nodes.append(block_node)
        elif block_type == BlockType.ORDERED_LIST:
            splitted_blocks = list(map(lambda x: x.split(),block.split("\n"))) 

            lines = []
            for sblock in splitted_blocks:
                sblock.remove(sblock[0])
                lines.append(" ".join(sblock))

            final_nodes = []
            for line in lines:
                children = text_to_children(line)
                final_nodes.append(ParentNode(tag="li", children=children))

            block_node = ParentNode(tag=determine_tag(block_type), children=final_nodes)
            block_nodes.append(block_node)
        else:
            lines = block.split("\n")
            paragraph = " ".join(lines)
            children = text_to_children(paragraph)
            block_node = ParentNode(tag=determine_tag(block_type), children=children)
            block_nodes.append(block_node)

    return block_nodes
    
def markdown_to_html_node(markdown):
    parent_node = ParentNode(tag="div", children=get_block_nodes(markdown))
    return parent_node


def copy_content(source, destination):
    #Remove public content
    destination_files = os.listdir(destination)
    if len(destination_files) > 0:
        for d_file in destination_files:
            d_path = os.path.join(destination, d_file)
            if os.path.isfile(d_path):
                os.remove(d_path)
            else:    
                shutil.rmtree(d_path)

    if os.path.exists(source):
        if os.path.isfile(source):
            shutil.copy(source, destination)
        else:
            source_files = os.listdir(source)
            for file in source_files:
                file_path = os.path.join(source, file)
                if os.path.isfile(file_path):
                    shutil.copy(file_path, destination)
                    continue
                else:
                    new_directory = os.path.join(destination, file)
                    os.mkdir(new_directory)
                    copy_content(file_path, new_directory)

        
                        


def extract_title(markdown):
    md = "".join(markdown_to_blocks(markdown)).split('\n') 
    header = None
    for line in md:
        if line.startswith("# "):
            header = line.lstrip('# ')
            break

    if header is None:
        raise Exception("There is no header in this markdown file.")
    return header

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    markdown = open(from_path).read()
    html_template = open(template_path).read()

    converted_markdown = markdown_to_html_node(markdown).to_html()

    title = extract_title(markdown)
    

    html_template = html_template.replace("{{ Title }}", title)
    html_template = html_template.replace("{{ Content }}", converted_markdown)


    dest_dir = os.path.dirname(dest_path)

    if dest_dir != "":
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w") as f:
        f.write(html_template)



    # html.replace("{{Title}}", title)
    # html.replace("{{Content}}", html)

def generate_html(from_path, template, basepath):
    markdown = open(from_path).read()
    html_template = open(template).read()

    converted_markdown = markdown_to_html_node(markdown).to_html()

    title = extract_title(markdown)
    html_template = html_template.replace("{{ Title }}", title)
    html_template = html_template.replace("{{ Content }}", converted_markdown)

    html_template = html_template.replace('href="/', f'href="{basepath}')
    html_template = html_template.replace('src="/', f'src="{basepath}')

    return html_template

def generate_pages_recursively(dir_path_content, template_path, dest_path, basepath):
    # template = open(template_path).read()

    if os.path.isfile(dir_path_content):
        print(f"Is file: {dir_path_content}")
        html = generate_html(dir_path_content, template_path, basepath)

        dest_path_lib = pathlib.Path(dest_path)

        dest_path = dest_path.replace(".md", ".html")

        with open(dest_path, "w") as f:
            f.write(html)

    else:
        # print(f"Is directory: {dir_path_content}")
        
        dir_files = os.listdir(dir_path_content)
        
        for dir_file in dir_files:
            path = pathlib.Path(os.path.join(dir_path_content, dir_file))
            
            new_path = os.path.join(dest_path, path.name)
            if not os.path.isfile(path):
                os.mkdir(os.path.join(dest_path, path.name))
            generate_pages_recursively(path, template_path, new_path, basepath)



        



        
        



    






