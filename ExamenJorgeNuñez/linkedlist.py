class Node:
    def __init__(self, value=None):
        self.value = value
        self.next = None
    
    def __str__(self):
        return str(self.value)

class LinkedList:
    def __init__(self):
        self.head = None
        
    def add_first(self, value):
        if not self.head:
            self.head = Node(value)
        else:
            new_node = Node(value)
            new_node.next = self.head
            self.head = new_node
            
    def add_in_position(self, value, i):
        if not self.head:
            self.head = Node(value)
        else:
            count = 1
            prev_node = None
            node = self.head
            while node and count < i + 1:
                if count == i:
                    if not prev_node:
                        aux_node = Node(value)
                        aux_node.next = self.head
                        self.head = aux_node
                    else:
                        aux_node = Node(value)
                        aux_node.next = node
                        prev_node.next = aux_node
                count = count + 1  
                prev_node = node
                node = node.next
            if not node and count < i + 1:
                prev_node.next = Node(value)
            
    def add_last(self, value):
        if not self.head:
            self.head = Node(value)
        else:
            node = self.head
            while node.next:
                node = node.next
            node.next = Node(value)
    
    def find(self, value):
        result = False
        if not self.head:
            return result
        else:
            node = self.head
            while node and not result:
                if node.value == value:
                    result = True 
                node = node.next
            return result

        
    def __contains__(self, value):
        result = False
        if not self.head:
            return result
        else:
            node = self.head
            while node and not result:
                if node.value == value:
                    result = True 
                node = node.next
            return result
        
    def get_node(self, value):
        result = None
        exit = False
        if not self.head:
            return result
        else:
            node = self.head
            while node and not exit:
                if node.value == value:
                    result = node.value
                    exit = True
                node = node.next
            return result
        
    def delete(self, value):
        if not self.head:
            print("The linked list is empty")
        else:
            node = self.head
            node_prev = None
            while node:
                if node.value == value:
                    #borrar el nodo
                    if not node_prev:
                        self.head = node.next
                    else:
                        node_prev.next = node.next
                node_prev = node
                node = node.next
            
    def print_linked_list(self):
        print("---- LINKED LIST ----")
        if not self.head:
            print("The list is empty")
        else:
            node = self.head
            while node:
                print(node.value)
                node = node.next
            print("---------------------")
            
    def delete_position(self, i):
        count = 1
        if not self.head:
            print("The list is empty")
        else:
            if i == 1:
                self.head = self.head.next
            else:
                prev_node = None
                node = self.head
                while node and count < i + 1:
                    if count == i:
                        if not prev_node:
                            self.head = node.next
                        else:
                            prev_node.next = node.next
                    prev_node = node
                    node = node.next
                    count += 1
    
    def dequeue_list(self):
        result = None
        if not self.head:
            print("The list is empty")
        else:
            result = self.head
            self.head = self.head.next
        return result
            
    
    def print_backwards_v1(self):
        print("---- LINKED LIST BACKWARDS V1 ---")
        if not self.head:
            print("The linked list is empty")
        else:
            node = self.head
            list_nodes = []
            while node:
                list_nodes.append(node)
                node = node.next
            for e in reversed(list_nodes):
                print(e)
    def length(self):
        total = 0
        node = self.head
        while node:
            total += 1
            node = node.next
        return total

    def get(self, index):
        if 0 <= index < self.length():
            node = self.head
            for _ in range(index):
                node = node.next
            return node.value
        else:
            raise IndexError(f"[get]: {index} index out of range")
    @staticmethod            
    def iterate_backwards(node):
        if node.next:
            LinkedList.iterate_backwards(node.next)
            print(node.value)
        else:
            print(node.value)
        
       
    def print_backwards_v2(self):
        print("---- LINKED LIST BACKWARDS V2 ---")
        if not self.head:
            print("The linked list is empty")
        else:
            LinkedList.iterate_backwards(self.head)        