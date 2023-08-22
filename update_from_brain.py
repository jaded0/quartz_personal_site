import os
import re

# Constants
SOURCE_DIR = "/home/jaden/Documents/brain"
DEST_DIR = "/home/jaden/Documents/quartz_personal_site/content"
PUBLISH_TAG = "#publish-this"

def get_tags_from_content(content):
    # Search for unescaped # symbols followed by non-space characters for tags
    tags = re.findall(r'(?<!\\)#(\w+)', content)
    
    # Remove the 'publish-this' tag from the list if it's present
    if "publish-this" in tags:
        tags.remove("publish-this")
    
    return tags

def has_frontmatter(content):
    return content.startswith('---')

def add_frontmatter(filename, content):
    tags = get_tags_from_content(content)
    
    # Create frontmatter
    frontmatter = '---\ntitle: "{}"\ntags:\n{}\n---\n'.format(
        filename.replace('.md', ''),
        '\n'.join(['- ' + tag for tag in tags])
    )
    
    return frontmatter + content

def process_file(filepath, dest_path):
    with open(filepath, 'r') as f:
        content = f.read()
        
        # Check if the file should be processed
        if PUBLISH_TAG in content:
            # Remove the publish tag
            content = content.replace(PUBLISH_TAG, "")
            
            # Check and add frontmatter if needed
            if not has_frontmatter(content):
                content = add_frontmatter(os.path.basename(filepath), content)
            
            # Write to the destination
            with open(dest_path, 'w') as dest_file:
                dest_file.write(content)

def main():
    for root, dirs, files in os.walk(SOURCE_DIR):
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                dest_path = os.path.join(DEST_DIR, filename)
                
                process_file(filepath, dest_path)
                
if __name__ == '__main__':
    main()

