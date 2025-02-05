import json
from collections import defaultdict

def output_analysis(rsef_output_path: str, output_summary_path: str):
    """Analyze the output of RSEF and save summary statistics to a JSON file."""
    print("Starting RSEF Output Analysis...")
    
    # Load the JSON file
    try:
        with open(rsef_output_path, 'r', encoding="UTF-8") as file:
            data = json.load(file)
            rsef_output = data.get('RSEF Output', [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading file: {e}")
        return
    
    # Ensure uniqueness of RSEF output
    unique_rsef_output = []
    for item in rsef_output:
        if item not in unique_rsef_output:
            unique_rsef_output.append(item)
    rsef_output = unique_rsef_output
    
    # Compute statistics
    num_papers = len(rsef_output)
    num_papers_with_code = sum(1 for paper in rsef_output if paper.get('implementation_urls'))
    
    num_unidir, num_bidir, num_both = 0, 0, 0
    git_links, zenodo_links = 0, 0
    bidir_locations = defaultdict(int)
    links_per_paper = defaultdict(int)
    
    for paper in rsef_output:
        implementation_urls = paper.get('implementation_urls', [])
        links_per_paper[len(implementation_urls)] += 1
        
        for implementation_url in implementation_urls:
            unidir, bidir = False, False
            for method in implementation_url.get('extraction_methods', []):
                if method.get('type') == 'unidir':
                    unidir = True
                    num_unidir += 1
                elif method.get('type') == 'bidir':
                    bidir = True
                    location_type = method.get('location_type', 'unknown')
                    bidir_locations[location_type] += 1
                    num_bidir += 1
            
            if implementation_url.get('type') == 'git':
                git_links += 1
            elif implementation_url.get('type') == 'zenodo':
                zenodo_links += 1
            
            if unidir and bidir:
                num_both += 1
    
    # Prepare summary statistics
    summary = {
        "total_papers": num_papers,
        "papers_with_repositories": num_papers_with_code,
        "extractions": {
            "total_unidirectional": num_unidir,
            "total_bidirectional": num_bidir,
            "both_methods": num_both
        },
        "repository_links": {
            "total_git_links": git_links,
            "total_zenodo_links": zenodo_links
        },
        "links_per_paper": {f"{key}_links": value for key, value in sorted(links_per_paper.items())},
        "bidirectional_extraction_locations": dict(bidir_locations)
    }
    
    # Save summary to a JSON file
    try:
        with open(output_summary_path, 'w', encoding="UTF-8") as outfile:
            json.dump(summary, outfile, indent=4)
        print(f"Summary statistics saved to {output_summary_path}")
    except IOError as e:
        print(f"Error saving summary: {e}")
