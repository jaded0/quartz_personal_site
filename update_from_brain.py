import os
import re

# Constants
SOURCE_DIR = "/home/jaden/Documents/brain"
DEST_DIR = "/home/jaden/Documents/quartz_personal_site/content"
PUBLISH_TAG = "#publish-this"

def get_tags_from_content(content):
    # Search for unescaped # symbols followed by non-space characters for tags
    tags = re.findall(r'(?<!\\)#(\w+)(?=\s|$)', content)
    
    # Remove the 'publish-this' tag from the list if it's present
    if "publish-this" in tags:
        tags.remove("publish-this")
    
    return tags

def remove_id_only_frontmatter(content):
    # Remove the id only frontmatter
    return re.sub(r'---\nid: .*\n---', '', content)

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
            
            # Remove the id only frontmatter
            content = remove_id_only_frontmatter(content)

            # Check and add frontmatter if needed
            if not has_frontmatter(content):
                content = add_frontmatter(os.path.basename(filepath), content)
            
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Write to the destination
            with open(dest_path, 'w') as dest_file:
                dest_file.write(content)

def main():
    for root, dirs, files in os.walk(SOURCE_DIR):
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                
                # Compute the relative path to maintain the same directory structure
                rel_path = os.path.relpath(filepath, SOURCE_DIR)
                dest_path = os.path.join(DEST_DIR, rel_path)
                
                process_file(filepath, dest_path)
                
if __name__ == '__main__':
    main()
