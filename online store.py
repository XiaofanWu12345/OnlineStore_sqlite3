# Xiaofan Wu 903152422

import sqlite3
class Owner:
    """The Owner class should have one class attribute db (initialized as None) which will represent a
    database connection object. Each owner instance should have instance variables that hold the 
    owner's unique name, money, and a dictionary of their inventory in the form {(item, price): count)}
    """
    db = None
    def __init__(self, name, starting_cash = 500):
        """money has an initital default value, but any other money amount can be 
        passed in to the init method. It is up to you you if you would like to have a 
        default parameter in init for InventoryDict, but you can also just instantiate 
        it in init.

        Parameters:
        self
        name: String
        money: int -- the Owner's money, is 500 if not given
        
        """
        self.name = name
        self.money = starting_cash
        self.InventoryDict = {}

    def __repr__(self):
        return str([self.money,self.InventoryDict])

    def buy_cheapest(self, item_name = None):
        """Buys the cheapest of the specified item, and if no item is specified,
            buys one of the cheapest items in the database. Reduce the owners money by the 
            item's price, decrease the count of that item in the database (or remove
            it if there's none left after you decrease the count), and add it to the
            owners inventoryDict.  When adding to the inventoryDict, if the owner
            has one of those items at the same price, increase the count.  If not, 
            add it to the inventoryDict with a count of 1. If the owner does not have
            enough money to buy what they passed in, or if they did not pass in anything,
            if they do not have enough money to buy the cheapest thing in the database,
            the database should print a message to the user that they do not have 
            sufficient funds and not add it to their inventory or remove it from the database.
            

        Parameters:
        self
        item_name: String -- the name of the item to be bought

        Return:
        None
        """
        db = Owner.db
        c = db.cursor()
        c.execute("select * from Inventory")
        if item_name != None:
            alist = [row for row in c.fetchall() if row[0].strip()==item_name]
            cheapitem = min(alist, key=lambda x:x[1])
        else:
            alist = [row for row in c.fetchall()]
            cheapitem = min(alist, key=lambda x:x[1])
        if self.money >= cheapitem[1]:
            self.money -= cheapitem[1]
            c = db.cursor()
            c.execute("update Inventory set Quantity=Quantity-1 where item_name=? and Price=? and Quantity>1", (cheapitem[0],cheapitem[1]))
            db.commit()
            c = db.cursor()
            c.execute("delete from Inventory where item_name=? and Price=? and Quantity=1",(cheapitem[0],cheapitem[1]))
            db.commit()
            tp = cheapitem[:2]
            if tp in self.InventoryDict.keys():
                self.InventoryDict[tp] += 1
            else:
                self.InventoryDict[tp] = 1
        else:
            print("Sorry, you do not have sufficient funds to buy things.")

    def sell_item(self, item_name = None):
        """Sells the most expensive of the specified item (from the owner's 
        inventory), and if no item is specified, sells the most expensive item
        in inventory. Increase the owners money by the price and add the item, 
        price to the database and set the count to 1 (unless the item is already
        in the database, in which case, you just increase the count of the
        most expensive). Then, decrease the count of that item (or remove
        it if the count is 1) from the inventoryDict. 
            


        Parameters:
        self
        item_name: String -- the name of the item to be bought

        Return:
        None
        """
        db = Owner.db
        if item_name != None:
            expensiveitem = max([k for k in self.InventoryDict.keys() if k[0].strip()==item_name], key=lambda x:x[1])
        else:
            expensiveitem = max([k for k in self.InventoryDict.keys()], key=lambda x:x[1])
        self.money += expensiveitem[1]
        c = db.cursor()
        c.execute("select item_name,Price from Inventory")
        if expensiveitem in c.fetchall():
            c = db.cursor()
            c.execute("update Inventory set Quantity=Quantity+1 where item_name=? and Price=?", expensiveitem)
            db.commit()
        else:
            c = db.cursor()
            c.execute("insert into Inventory values(?,?,?)",(expensiveitem[0],expensiveitem[1],1))
            db.commit()
        if self.InventoryDict[expensiveitem] > 1:
            self.InventoryDict[expensiveitem] -= 1
        else:
            del self.InventoryDict[expensiveitem]

    def fire_sale(self):
        """Sells everything in inventory.  Remove everything from your
         inventoryDict and add it all to the database (if the item is 
         already in the database just increase the count, and if not make 
         sure to add a new row in for the item).
         Update the owners money accordingly.
         

        Parameters:
        self

        Return:
        None
        """
        db = Owner.db
        for item in self.InventoryDict.keys():
            count = self.InventoryDict[item]
            self.money += item[1] * count
            c = db.cursor()
            c.execute("select item_name,Price from Inventory")
            if item in c.fetchall():
                c = db.cursor()
                c.execute("update Inventory set Quantity=Quantity+? where item_name=? and Price=?", (count,item[0],item[1]))
                db.commit()
            else:
                c = db.cursor()
                c.execute("insert into Inventory values(?,?,?)",(item[0],item[1],count))
                db.commit()
        self.InventoryDict = {}

    def net_worth(self):
        """Returns the total net worth of the Owner, which is the amount of
        money they have plus the sum of the value of everything in their inventory.

        Parameters:
        self

        Return:
        int -- the amount of money the user has plus the sum of the value of everything in 
                 inventory
        """
        num = self.money + sum([k[1] for k in self.InventoryDict.keys()])
        return num

    def buy_all(self, item_name = None):
        """Buys all available items of the specified item. If no item is given,
         defaults to the item with the lowest cost for the sum of all the prices
         of items with that name of that item. Update the database, inventoryDict,
         and the owners money.
         

        Parameters:
        self
        item_name: String -- name of the item to buy

        Return:
        None
        """
        db = Owner.db
        if item_name == None:
            alist = []
            c = db.cursor()
            c.execute("select * from Inventory")
            for i in c.fetchall():
                if i[0] not in alist:
                    alist.append(i[0])
            c = db.cursor()
            c.execute("select * from Inventory")
            cl = list(c.fetchall())
            item_name = min(alist, key=lambda name:sum([i[1]*i[2] for i in cl if i[0].strip()==name.strip()]))
        c = db.cursor()
        c.execute("select * from Inventory")
        itemlist = [row for row in c.fetchall() if row[0].strip() == item_name]
        cheapitem = min(itemlist, key=lambda x:x[1]) #simply to have the function run into error if item_name is not in the database
        total_price = sum([i[1]*i[2] for i in itemlist])
        if self.money >= total_price:
            for item in itemlist:
                count = item[2]
                price = item[1]*count
                self.money -= price
                c = db.cursor()
                c.execute("update Inventory set Quantity=Quantity-? where item_name=? and Price=? and Quantity>?", (count,item_name,item[1],count))
                db.commit()
                c = db.cursor()
                c.execute("delete from Inventory where item_name=? and Price=? and Quantity=?",(item_name,item[1],count))
                db.commit()
                tp = item[:2]
                if tp in self.InventoryDict.keys():
                    self.InventoryDict[tp] += count
                else:
                    self.InventoryDict[tp] = count
        else:
            print("Sorry, you do not have sufficient funds to buy things.")
          
import csv
def create_db(file_name):
    """Creates a local SQLite database using the sqlite3 module and then creates a table called 
    Inventory in the database. The table should be populated from a csv file. There will be three 
    columns: item_name, Price, and Quantity. The composite key of the table will be (item_name, price). 
    Price and Quantity will both be stored as integers in the database.

    Parameters:
    file_name: String -- the name of the csv file that contains the inventory

    Return:
    a connection to the created database
    """
    with open(file_name,'r') as f:
        r = csv.reader(f)
        clist = [tuple([line[0],int(line[1]),int(line[2])]) for line in list(r)[1:]]
        print(clist)
    db = sqlite3.connect(':memory:')
    c = db.cursor()
    c.execute("create table Inventory(item_name text not null, Price integer not null, Quantity integer not null, primary key(item_name,Price))")
    c.executemany("insert into Inventory values(?,?,?)",clist)
    db.commit()
    return db

def main(args):
    """ Create a main function that first calls create_db to create a local database containing a 
    table called Inventory and populates it with the contents of a csv file. The CSV filename should be 
    passed in as an argument to the main function through the command line. Then the main function should 
    allow the user to create as many owners as they want to. You need to keep track of those owners (in a 
    dictionary), as the user should be allowed to select any owner at any point, and call the various 
    functions on them. 
    
    Your main method should have a prompt that asks the user which which of the operations they want to call
    then from there, there should be a prompt asking which of the one of the owners they want to select. The
    user may not know the item names in the Inventory table, and if this is the case, 
    they should be able to prompt the main function to provide a list of all of the inventory names in the
    Inventory table, with no duplicates. At any point, the user should be able to go quit out of 
    the program. Remember to close your database connection.
    """
    Owner.db = create_db(args[1])
    a = True
    olist = {}
    while a:
        d = input("What would you like to do next?")
        if d.lower() == 'quit':
            a = False
        elif d.lower() == "create owner":
            name = input("Great! What's your owner's name?")
            if name.lower() != 'quit':
                money = input("How much money does your owner have?")
                if money.lower() != 'quit':
                    if money != '':
                        money = int(money)
                        owner = Owner(name,money)
                    else:
                        owner = Owner(name)
                    olist[name.lower()] = owner
                else:
                    a = False
            else:
                a = False
        elif d.lower() == "buy inventory":
            name = input("Which owner do you want to buy inventory for?")
            if name.lower() != 'quit':
                item_name = input("Great! Do you know the item name?")
                if item_name.lower() != 'quit':
                    b = input("Would you like to buy cheapest or buy all?")
                    if b != 'quit':
                        if b.lower() == 'buy cheapest':
                            try:
                                if item_name == '':
                                    olist[name.lower()].buy_cheapest()
                                else:
                                    olist[name.lower()].buy_cheapest(item_name.lower())
                            except:
                                print("Sorry, the item you want to buy doesn't exist in the database.")                        
                        elif b.lower() == 'buy all':
                            try:
                                if item_name == '':
                                    olist[name.lower()].buy_all()
                                else:
                                    olist[name.lower()].buy_all(item_name.lower())
                            except:
                                print("Sorry, the item you want to buy doesn't exist in the database.")
                    else:
                        a = False
                else:
                    a = False
            else:
                a = False
        elif d.lower() == "sell inventory":
            name = input("Which owner do you want to sell inventory for?")
            if name.lower() != 'quit':
                s = input("Would you like to sell the most expensive item or sell all items?")
                if s.lower() != 'quit':
                    if s.lower() in "sell all items":
                        olist[name.lower()].fire_sale()
                    elif s.lower() in "sell the most expensive item":
                        item_name = input("Great! Do you know the item name?")
                        if item_name.lower() != 'quit':
                            try:
                                if item_name == '':
                                    olist[name.lower()].sell_item()
                                else:
                                    olist[name.lower()].sell_item(item_name.lower())
                            except:
                                print("Sorry. You're selling something not in your inventory.")
                        else:
                            a = False
                else:
                    a = False
            else:
                a = False
        elif d.lower() == "net worth":
            name = input("Which owner do you want to calculate the net worth?")
            if name.lower() != 'quit':
                n = olist[name.lower()].net_worth()
                print("The net worth of {} is {}.".format(name,n))
            else: 
                a = False
    if name.lower() != 'quit':
        print("Thanks for playing, {}!".format(name))
    else:
        print("Thanks for playing!")
    print(olist)



if __name__ == "__main__":
    import sys
    main(sys.argv)









 














