from functions import copy_content, generate_page, generate_pages_recursively
import sys

def main():
    copy_content("static", "docs")
    basepath = "/" if len(sys.argv) == 1 else sys.argv[1] 
    generate_pages_recursively("content", "template.html", "docs", basepath)





    
    


    


main()
