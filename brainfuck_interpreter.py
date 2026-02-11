import argparse
import os
import sys

def tokenize_brainfuck_script(input_string: str):
    tokens = list()

    i = 0
    loop_precalculation = list()
    loop_table = dict()
    token_index_calc = 0
    while i < len(input_string):
        char = chr(input_string[i])

        if char in '<>+-':
            count = 1
            while i + 1 < len(input_string) and input_string[i + 1] == char:
                count += 1
                i += 1
            
            tokens.append((str(char), int(count)))
            token_index_calc += 1
        elif char == '[':
            loop_precalculation.append(token_index_calc)
            tokens.append(('[', token_index_calc))
            token_index_calc += 1
        elif char == ']':
            if not loop_precalculation:
                raise SyntaxError('End of loop detected without start.')
            get_loop = int(loop_precalculation.pop())
            loop_table[get_loop] = token_index_calc
            tokens.append((']', get_loop))
            token_index_calc += 1
        elif char in ',.':
            tokens.append((str(char), None))
            token_index_calc += 1
        else:
            pass
        
        i += 1
    
    if loop_precalculation:
        raise SyntaxError('Start of loop detected without end.')
    
    return tokens, loop_table

def execute_brainfuck(token_list: list, loop_table: dict, max_tape_size: int):
    #> Initiate some variables
    bf_data = [0] * 1000
    current_pointer = 0
    
    #> Iterate over tokens and execute
    token_index = 0
    while token_index < len(token_list):
        current_token, token_meta = token_list[token_index]

        if current_token == '>':
            current_pointer += token_meta
            while current_pointer >= len(bf_data):
                bf_data.extend([0] * 500)
                if max_tape_size != -1 and len(bf_data) > max_tape_size:
                    raise OverflowError(f'Maximum tape size is {max_tape_size}.')
        elif current_token == '<':
            current_pointer -= token_meta
            if current_pointer < 0:
                raise IndexError('Pointer is pointing below zero.')
        elif current_token == '+':
            bf_data[current_pointer] += token_meta
            bf_data[current_pointer] %= 256
        elif current_token == '-':
            bf_data[current_pointer] -= token_meta
            bf_data[current_pointer] %= 256
        elif current_token == '.':
            print_char = chr(bf_data[current_pointer])
            sys.stdout.write(print_char)
            if print_char == '\n':
                sys.stdout.flush()
        elif current_token == ',':
            sys.stdout.flush()
            bf_data[current_pointer] = ord(sys.stdin.read(1) or '\x00')
        elif current_token == '[' and bf_data[current_pointer] == 0:
            token_index = loop_table[token_meta]
        elif current_token == ']' and bf_data[current_pointer] != 0:
            token_index = token_meta
        else:
            pass
        
        token_index += 1

if __name__ == '__main__':
    
    #> Set argument parser
    arg_parser = argparse.ArgumentParser('Python Simple Brainfuck Interpreter')
    arg_parser.add_argument('input_file', metavar='Input File', type=str, help='Input File Path')
    arg_parser.add_argument('--tape-size', type=str, help='Change maximum tape size, default is 10,000,000. -1 for infinite 😈.', default='10000000')

    parsed_args = arg_parser.parse_args()

    input_file_arg = parsed_args.input_file
    max_tape_size = int(parsed_args.tape_size)

    if not os.path.isfile(input_file_arg):
        print(f'{input_file_arg} is not a file.')
        sys.exit(1)

    with open(input_file_arg, 'rb') as f:
        loaded_script = f.read()
    
    if len(loaded_script) == 0:
        sys.exit()

    token_list, loop_table = tokenize_brainfuck_script(loaded_script)
    execute_brainfuck(token_list, loop_table, max_tape_size)
