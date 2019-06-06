from tkinter import *

from flask import Flask, jsonify, request, send_from_directory
import time
import math
from math import pi
import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft

from blockchain import Blockchain
from utility.verification import Verification
from wallet import Wallet
import random
import os
import sys
node_id=0
sel_node=0
node=[]
prim_node_id=0
c_speed=300000008
live_nodes=[]
avail_freq=[80,20,30,40,50,60,70,80,90,100]
used_freq={}
modulated_waves={}
freq_info={}
PU_img=0
SU_img=0
prim_live_nodes=[]
primary_wallets=[]
prim_node=[]
values = {'node_id': node_id, 'snr':[10,20,30,40,50,60,70,80,90]}
#values={'node_id':node_id,'snr':{'A':20,'B':30,'C:40}}

class Prim_Node():
    def __init__(self,user_node_id,location):
        global SU_img
        global prim_live_nodes 
        prim_live_nodes.append(prim_node_id)
        prim_live_nodes[node_id]=canvas.create_image(10,10, anchor=NW, image=SU_img)
        self.location=location
        self.Fc=avail_freq[0]
        used_freq[node_id]=self.Fc
        avail_freq.pop(0)
        canvas.coords(prim_live_nodes[node_id],[self.location[0],self.location[1]])
        self.N=600
        self.T=1.0/800.0
        self.Fm=5
        self.Ac=5
        self.Am=2
        self.t_gain=2
        self.r_gain=2
        self.t = np.linspace(0.0, self.N*self.T, self.N)
        self.tf = np.linspace(0.0, 1.0/(2.0*self.T), self.N//2)
        self.transmission_power=20
        self.t_gain=2
        self.r_gain=2
        self.carrier=np.cos(2*pi*self.Fc*self.t)
        self.message=np.cos(2*pi*self.Fm*self.t)
        self.km=self.Am/self.Ac
        self.Pc=pow(self.Ac,2)/2
        self.Pt=self.Pc*(1+((self.km)**2)/2)
        self.mod=self.Ac*(1+self.km*(self.message))*self.carrier

    #def get_freq():


class Node():
    def __init__(self,node_id,location):
        global blockchain
        global primary_wallets
        global PU_img
        global live_nodes
        global modulated_waves
        global node
        global wallet
        live_nodes.append(node_id)
        live_nodes[node_id]=canvas.create_image(10,10, anchor=NW, image=PU_img)
        self.node_id=node_id
        self.location=location
        canvas.coords(live_nodes[node_id],[self.location[0],self.location[1]])
        print("node has been created sir")
        self.N=600
        self.T=1.0/800.0
        self.Fm=5
        self.Ac=5
        self.Am=2
        self.Fc=0
        #used_freq[node_id]=self.Fc
        #avail_freq.pop(0)
        self.t = np.linspace(0.0, self.N*self.T, self.N)
        self.tf = np.linspace(0.0, 1.0/(2.0*self.T), self.N//2)
        self.transmission_power=20
        self.t_gain=2
        self.r_gain=2
        self.carrier=np.cos(2*pi*self.Fc*self.t)
        self.message=np.cos(2*pi*self.Fm*self.t)
        self.km=self.Am/self.Ac
        self.Pc=pow(self.Ac,2)/2
        self.Pt=self.Pc*(1+((self.km)**2)/2)
        self.mod=self.Ac*(1+self.km*(self.message))*self.carrier
        modulated_waves[self.Fc]=self.mod
        self.mod_fft=fft(self.mod)
        primary_wallets.append(node_id)
        self.port=5000+node_id
        os.system("gnome-terminal -e 'bash -c \"python node.py -p {}; exec bash\"'".format(5000+self.node_id))
        wallet=Wallet(self.port)
        primary_wallets[node_id]=wallet
        wallet.create_keys()
        print("Wallet created Now saving the keys")
        if wallet.save_keys():
            global blockchain
            print("Blockchain created for node",self.port)
            blockchain=Blockchain(wallet.public_key,self.port)

            #print("public key for node_id "+str(self.port)+" created")
        else:
            print("creating wallet failed")

           
                 

    def load_prim_keys(self):
        global blockchain
        global wallet
        if wallet.load_keys():
            blockchain = Blockchain(wallet.public_key, self.port)
            response = {
                'public_key': wallet.public_key,
                'private_key': wallet.private_key,
                'funds': blockchain.get_balance()
            }
            print(response)
        else:
            response = {
                'message': 'Loading the keys failed.'
            }   
            print(response)

    def prim_add_transaction(self):
        global blockchain
        global wallet
        global node
        self.values
        if wallet.public_key == None:
            response = {
                'message': 'No wallet set up.'
            }
            print(str(response))
        print("values are in prim_add_transac ")
        print(self.values)
        snr=self.values['snr']
        recipient=0
        amount=0
        signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
        print(signature)
        success = blockchain.add_transaction(
            self.port,snr,recipient, wallet.public_key, signature, amount)
        if success:
            response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'recipient': recipient,
                'amount': amount,
                'snr':snr
            },
            'funds': blockchain.get_balance()
            }
            print(str(response))
        else:
            response = {
                'message': 'Creating a transaction failed.'
            }
            print(str(response))

    def mine(self):
        global blockchain
        for j in range(len(node)):
            if(j==node_id):
                continue
            blockchain.add_peer_node(j+5000)
        if blockchain.resolve_conflicts:
            response = {'message': 'Resolve conflicts first, block not added!'}
            print(str(response))
        self.block = blockchain.mine_block()
        if self.block != None:
            dict_block = self.block.__dict__.copy()
            dict_block['transactions'] = [
                tx.__dict__ for tx in dict_block['transactions']]
            response = {
                'message': 'Block added successfully.',
                'block': dict_block,
                'funds': blockchain.get_balance()
            }
            print(str(response))
        else:
            response = {
            'message': 'Adding a block failed.',
            'wallet_set_up': wallet.public_key != None
            }
        self.clone()    
        print(str(response))

    def find_fft(self):
        global prim_node
        global used_freq
        R=0
        all_mod=0
        for i in range(len(used_freq)):
            R=math.sqrt((prim_node[i].location[0]-self.location[0])**2+(prim_node[i].location[1]-self.location[1])**2)
            if(R==0):
                continue
            print("value of R is ",R)
            mod=prim_node[i].Ac*(1+prim_node[i].km*(prim_node[i].message))*prim_node[i].carrier/(4*math.pi*R*node[i].Fc)   
            all_mod=all_mod+mod
        all_mod_fft=fft(all_mod)        
           
        plt.figure(1)
        plt.plot(self.tf, 2.0/self.N * np.abs(all_mod_fft[0:self.N//2]))
        plt.grid()
        plt.show()
        
    def receiver(self):
        global live_node
        global prim_node
        global c_speed
        #this is the reAcnow the signal level at a particular node this quation will 
        # be used to caAc
        result=0
        print("no. of live nodes is ",live_nodes)
        for i in range(len(prim_node)):
            R=math.sqrt((prim_node[i].location[0]-self.location[0])**2+(prim_node[i].location[1]-self.location[1])**2)
            if(R==0):
                continue
            print("value of R is ",R)
            result=result+(prim_node[i].Pt)*(prim_node[i].t_gain)*self.r_gain*c_speed*c_speed/pow((4*math.pi*prim_node[i].Fc*R),2)

        print("Recieved signal strength is"+str(result)+" DB")              

    def update_blockchain(self):
        global live_nodes
        global prim_nodeAc
        global c_speed
        self.values={}
        array=[]
        self.values['node_id']=self.node_id
        array.append(self.location[0])
        array.append(self.location[1])
        for i in range(len(prim_node)):
            R=math.sqrt((prim_node[i].location[0]-self.location[0])**2+(prim_node[i].location[1]-self.location[1])**2)
            if(R==0):
                continue
            print("value of R is ",R)
            freq_info=(prim_node[i].Pt)*(prim_node[i].t_gain)*self.r_gain*c_speed*c_speed/pow((4*math.pi*prim_node[i].Fc*R),2)
            tan_theta=(prim_node[i].location[1]-self.location[1])/(prim_node[i].location[0]-self.location[0])
            theta=math.atan(tan_theta)
            array.append(theta)
            freq_info=math.log(freq_info,10)
            array.append(freq_info)
        self.values['snr']=array
        print("the final blockchain data to be updated by each node is ")
        print(self.values)

    def clone(self):
        global node
        node_id=len(node)-1
        print("node id right now is ",node_id)
        for i in range(5000, 5000+node_id):   
            with open('blockchain-{}.txt'.format(5000+node_id), mode='r') as f:
                print("value of i is ",i)
                with open('blockchain-{}.txt'.format(i), mode='w') as g:
                    for line in f:
                        g.write(line)    

     

class pythongui:
    
    def __init__(self,master):
        frame=Frame(master)
        frame.pack()
        global PU_img
        global SU_img

        self.printButton = Button(frame,text="Left",command=self.left)
        self.printButton.pack(side=LEFT)
        
        self.printButton = Button(frame,text="Right",command=self.right)
        self.printButton.pack(side=LEFT)

        self.printButton = Button(frame,text="Up",command=self.up)
        self.printButton.pack(side=LEFT)

        self.printButton = Button(frame,text="Down",command=self.down)
        self.printButton.pack(side=LEFT)

        self.quitButton = Button(frame,text="Init",command=self.init)
        self.quitButton.pack(side=LEFT)

        self.printButton = Button(frame,text="Create_node",command=self.create_node)
        self.printButton.pack(side=LEFT)

        self.printButton = Button(frame,text="Select_node",command=self.select_node)
        self.printButton.pack(side=LEFT)

        self.printButton = Button(frame,text="Signal_strength",command=self.receiver_c)
        self.printButton.pack(side=LEFT)

        self.printButton = Button(frame,text="Update_blockchain",command=self.update_blockchain)
        self.printButton.pack(side=LEFT)

        self.printButton = Button(frame,text="mine_block",command=self.mine_block)
        self.printButton.pack(side=LEFT)

        self.printButton = Button(frame,text="create_prim_node",command=self.create_prim_node)
        self.printButton.pack(side=LEFT)

        PU_img = PhotoImage(file="PU_small.ppm")
        SU_img = PhotoImage(file="SU_small.ppm")

        self.prim_one=0

    def mine_block(self):
        global node
        node[sel_node].mine()

    def sim(node_id):
        if(node_id>20):
            while(True):
                x=random.randint(40,60)
                t.sleep(x)
                freq=used_
                used_freq
                avail_freq
                x=random.randint(40,60)
        #else:



    def update_blockchain(self):
        global node
        global sel_node
        for i in range(len(node)):
            node[i].update_blockchain()
            val=node[i].values
            print("values in up bc func are")
            print(val)
            node[i].prim_add_transaction()


    def receiver_c(self):
        global node
        global sel_node
        #node[sel_nAc
        node[sel_no].find_fft()

    def select_node(self):
        global live_nodes
        global node 
        global sel_node
        sel_node+=1
        sel_node=sel_node%len(live_nodes)
        self.prim_one=live_nodes[sel_node]
        print("selected node is",sel_node)    
        

    def create_prim_node(self):
        global prim_node_id
        global prim_node
        if(len(avail_freq)==0):
            print("all frequencies are occupied .. no free frequeAcncy thus node cannot be created")
            return
        prim_node.append(prim_node_id)
        x=random.randint(200,600)
        y=random.randint(200,600)
        prim_node[prim_node_id]=Prim_Node(prim_node_id,[x,y])   
        prim_node_id+=1
        print("Primary Node id is ",prim_node_id) 
        #t = Thread(target=sim, args=(user_node_id,))
        #t.start()       
    
    def create_node(self):
        global node_id
        global node
        node.append(node_id)
        x=random.randint(200,600)
        y=random.randint(200,600)
        node[node_id]=Node(node_id,[x,y])

        #t = Thread(target=sim, args=(user_node_id,))
        #t.start()
        
        node_id+=1
        print("Node id is ",node_id)

    def init(self):
        print("Initialising")
        canvas.coords(self.prim_one,[0,0,50,50])

    def left(self):
        global sel_node
        global node
        print("Hey,This Works Man")
        canvas.move(self.prim_one,-10,0)
        co_ordinates=canvas.coords(self.prim_one)
        node[sel_node].location=canvas.coords(self.prim_one)
        print(co_ordinates)

    def right(self):
        global sel_node
        global node
        print("Hey,This Works Man")
        canvas.move(self.prim_one,10,0)
        co_ordinates=canvas.coords(self.prim_one)
        node[sel_node].location=canvas.coords(self.prim_one)
        print(co_ordinates)
        
    def up(self):
        global sel_node
        global node
        print("Hey,This Works Man")
        canvas.move(self.prim_one,0,-10)
        co_ordinates=canvas.coords(self.prim_one)
        node[sel_node].location=canvas.coords(self.prim_one)
        print(co_ordinates)
        

    def down(self):
        global sel_node
        global node
        print("Hey,This Works Man")
        canvas.move(self.prim_one,0,10)
        co_ordinates=canvas.coords(self.prim_one)
        node[sel_node].location=canvas.coords(self.prim_one)
        print(co_ordinates)        

if __name__=="__main__":
    root=Tk()
    b=pythongui(root)
    canvas=Canvas(root,width=900,height=900)
    canvas.pack()
    root.mainloop()