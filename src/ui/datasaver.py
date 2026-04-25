import sys
import os

class datasaver:
    file_path = ''
    def __init__(self):
        pass
    
    def set_file_path(self,path):
        self.file_path = path
        return os.path.exists(path)
    
    def clear_lines(self):
        with open(self.file_path, 'w', encoding='utf-8') as file:
            pass
        
    def cut_lines(self,start,end):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open(self.file_path, 'w', encoding='utf-8') as file:
            for current_line, line in enumerate(lines):#, start=1):
                if current_line < start or current_line > end:
                    file.write(line)
    
    def line_num(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            file.close()
            return len(lines)
        return 0

    def get_line(self,pos):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for current_line, l in enumerate(lines):#, start=1):
                if current_line == pos:
                    return lines[pos]
        return ""

    def new_line(self,line):
        with open(self.file_path, 'a', encoding='utf-8') as file:
            file.write(line)
            file.write('\n')
            file.close()

    def get_line_nums(self,pos):
        line = self.get_line(pos)
        nums = [float(num) for num in line.split()]
        return nums
    
    def new_line_nums(self,nums):
        line =  ' '.join(map(str, nums))
        self.new_line(line)
        
    def print_file(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.read()
            print(lines)
            file.close()
            
    def get_buf(self):
        buf = []
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for current_line, l in enumerate(lines):
                nums = [float(num) for num in l.split()]
                buf.append(nums)
        return buf
        
            
if __name__ == "__main__":        
    ds =  datasaver()
    ds.set_file_path("./001.txt")
    ds.clear_lines()
    #ds.new_line("[0,0,0,0,0,0]")
    ds.new_line_nums([0,0,0,0,0,0])
    ds.new_line_nums([1,0,0,0,0,0])
    ds.new_line_nums([2,0,0,0,0,0])
    ds.cut_lines(0,0)
    ds.print_file()

    print("line",ds.get_line(0))
    print("nums",ds.get_line_nums(0))
    
    ds.set_file_path("./002.txt")
    ds.new_line_nums([12,0,0,0,0,0])
    ds.print_file()