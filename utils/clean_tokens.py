def clean_tokens(tokens):
    """
    Clean tokens by removing irrelevant characters but keep meaningful short tokens like 'M', 'F', etc.
    """
    preserve_short_tokens = ['M', 'F', 'X', 'Y', 'Z']
    
    cleaned_tokens = []
    for token in tokens:
        if token.isalnum() and (len(token) > 2 or token.upper() in preserve_short_tokens):
            cleaned_tokens.append(token)
    
    return cleaned_tokens
