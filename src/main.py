from functions import copy_content, generate_page, generate_pages_recursively
import sys

def main():
    copy_content("static", "docs")
    basepath = "/" if sys.argv is None else sys.argv 
    generate_pages_recursively("content", "template.html", "docs", basepath)





    
    


    


main()
