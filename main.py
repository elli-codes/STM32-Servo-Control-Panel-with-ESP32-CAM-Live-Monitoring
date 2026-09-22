from tkinter import*
import serial
import requests
import threading
from PIL import Image,ImageTk
from io import BytesIO

class my_class:
    def __init__(self):
        self.buffer=b""
        
        
        self.root=Tk()
        self.root.geometry("660x500+200+200")
        self.root.config(bg="#d3d3d3")
        self.root.title("Servo Motor Control Panel")

        self.txt20= Label(self.root)
        self.txt20.pack()
        self.txt20.place(x=150,y=150)

        
       
        self.txt2=Label(self.root,text="Please Enter your password to access the panel ", font=("segoe UI",16))
        self.txt2.pack()
        self.txt2.place(x=85 ,y=10)

        self.e1=Entry(self.root,width=20)
        self.e1.pack()
        self.e1.place(x=250,y=60)

        self.b1=Button(self.root,text="check password",font=("segoe UI",10))
        self.b1.pack()
        self.b1.place(x=260 ,y=90)
        self.b1.config(command=self.password)

        ###################################################################
    def camera_request(self):
            result=requests.get("http://192.168.137.60:81/stream",stream=True)
        
            self.chunks=result.iter_content(chunk_size=8192)
            self.camera()
        
        
    def camera(self):
         chunks=next(self.chunks)
         self.buffer+=chunks
            
            
         position=self.buffer.find(b"\r\n\r\n")
            
         if (position==-1):
            self.root.after(1,self.camera)
            return
         else:
            header=self.buffer[:position]
                
         content=header.find(b"Content-Length:")
         a=len(b"Content-Length:")
         number_start = content + a
         end = header.find(b"\r\n", number_start)
         content_num=header[number_start:end]
         content_number=int (content_num)
         jpeg=self.buffer[position+4:]
         jpeg_size=len(jpeg)
            
         if (jpeg_size < content_number):
            self.root.after(1, self.camera)
            return
         if (jpeg_size == content_number):
            part1=jpeg[:content_number]
            image_data = BytesIO(part1)
            image=Image.open(image_data)
               #print (type(image))
            photo = ImageTk.PhotoImage(image)
            self.img=photo
            self.txt20.config(image=self.img)
            self.buffer=b""
            self.root.after(1, self.camera)

               
         if (jpeg_size> content_number):
                
            part1=jpeg[:content_number]
            image_data = BytesIO(part1)
            image=Image.open(image_data)
            photo = ImageTk.PhotoImage(image)
            self.img=photo
            self.txt20.config(image=self.img)

                
                
            end_frame=(position+4)+content_number
            self.buffer=self.buffer[end_frame:]
            self.root.after(1, self.camera)
        

            

    def password(self):
        p=self.e1.get()
        if (p=="eli2026"):
            self.ser=serial.Serial("COM13",9600)
            self.ser.write("right\r".encode())

            #0 dergree
            self.b2=Button(self.root,text="0 degree",font=("segoe UI",12))
            self.b2.pack()
            self.b2.place(x=120 , y=400)
            self.b2.config(command=self.s0degree)
            #90 degree
            self.b3=Button(self.root,text="90 degree",font=("segoe UI",12))
            self.b3.pack()
            self.b3.place(x=260 , y=400)
            self.b3.config(command=self.s90degree)
            
            self.b4=Button(self.root,text="180 degree",font=("segoe UI",12))
            self.b4.pack()
            self.b4.place(x=400 , y=400)
            self.b4.config(command=self.s180degree)

            #real time stream
            thread1 = threading.Thread(target=self.camera_request)
            thread1.start()
            
            
        else:
            ser=serial.Serial("COM13",9600)
            ser.write("wrong\r".encode())


    def s0degree(self):
        #ser=serial.Serial("COM13",9600)
        self.ser.write("sefr degree\r".encode())
    def s90degree(self):
        #ser=serial.Serial("COM13",9600)
        self.ser.write("navad degree\r".encode())
    def s180degree(self):
        #ser=serial.Serial("COM13",9600)
        self.ser.write("sad degree\r".encode())
    
def main():
    x=my_class()
    x.root.mainloop()
if __name__=="__main__":main()    

















