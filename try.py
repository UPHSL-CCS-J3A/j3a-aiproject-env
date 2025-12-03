status = True
class myStatus:
    def __init__(self, status):
        self.status = status
    def change(self):
        self.status = False

new_status = myStatus(status)
new_status.change()
print(status)
print(new_status.status)
