import pkgutil


# A simple skills list — extend this as needed
DEFAULT_SKILLS = [
'python', 'java', 'c++', 'c#', 'javascript', 'react', 'angular', 'node.js',
'flask', 'django', 'sql', 'postgresql', 'mysql', 'mongodb', 'aws', 'azure',
'docker', 'kubernetes', 'html', 'css', 'git', 'rest', 'graphql', 'machine learning',
'deep learning', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'
]




def load_skills_list():
    # For now return the DEFAULT_SKILLS. Later you can load from file or DB.
    return DEFAULT_SKILLS