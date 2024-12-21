class Item:
    def __init__(self, v: int, next_item: 'Item' = None):
        self.value = v
        self.next = next_item

    def __str__(self):
        return f'{self.value} -> {self.next}'


head = Item(0)
for i in range(1, 5):
    head = Item(i, head)


def rev(item: Item) -> Item:
    new_head = None

    while item:
        if item.next is None:
            item.next = new_head
            break

        next_item = item.next
        item.next = new_head
        new_head = item
        item = next_item

    return item


print('Before reverse:')
print(head)
head = rev(head)
print('After reverse:')
print(head)
