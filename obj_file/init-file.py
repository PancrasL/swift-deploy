import random,sys

def random_str(length):
    return ''.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a'], length))

'''
@param size   total file size
@param length each string size
''' 
def gen_file(path, size, length):
    with open(path, 'w') as f:
        for i in range(0, size, length):
            f.write(random_str(length))

if __name__ == '__main__':
    gen_file(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))