def check_brackets(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    stack = []
    line = 1
    col = 1
    
    # Simple state machine to skip comments and strings
    in_string = False
    string_char = None
    in_line_comment = False
    in_block_comment = False
    
    i = 0
    n = len(content)
    while i < n:
        char = content[i]
        
        # Track line/col
        if char == '\n':
            line += 1
            col = 1
        else:
            col += 1
            
        if in_line_comment:
            if char == '\n':
                in_line_comment = False
            i += 1
            continue
            
        if in_block_comment:
            if char == '*' and i + 1 < n and content[i+1] == '/':
                in_block_comment = False
                i += 2
                col += 1
            else:
                i += 1
            continue
            
        if in_string:
            if char == '\\': # skip escaped char
                i += 2
                col += 1
                continue
            if char == string_char:
                in_string = False
            i += 1
            continue
            
        # Check comments
        if char == '/' and i + 1 < n and content[i+1] == '/':
            in_line_comment = True
            i += 2
            col += 1
            continue
        if char == '/' and i + 1 < n and content[i+1] == '*':
            in_block_comment = True
            i += 2
            col += 1
            continue
            
        # Check strings (single, double quotes and backticks)
        if char in ["'", '"', '`']:
            in_string = True
            string_char = char
            i += 1
            continue
            
        # Track brackets
        if char in ['{', '[', '(']:
            stack.append((char, line, col))
        elif char in ['}', ']', ')']:
            if not stack:
                print(f"Error: unmatched closing '{char}' at line {line}, col {col}")
                return False
            top, l, c = stack.pop()
            if (char == '}' and top != '{') or \
               (char == ']' and top != '[') or \
               (char == ')' and top != '('):
                print(f"Error: mismatched brackets: closed '{char}' at line {line}, col {col} but opened '{top}' at line {l}, col {c}")
                return False
                
        i += 1
        
    if stack:
        print(f"Error: unmatched open brackets at end of file:")
        for top, l, c in stack[-5:]:
            print(f"  '{top}' opened at line {l}, col {c}")
        return False
        
    print("Success: all braces/brackets/parentheses match correctly!")
    return True

check_brackets('app.js')
