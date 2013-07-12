import os,sys
from ctypes import CDLL

#if sys.platform.startswith('win'):
#   lib_ext = '.dll'
#elif sys.platform == 'darwin':
#   lib_ext = '.dylib'
#else:
#   lib_ext = '.so'
#gcc -std=c99 iio.c -shared -o iio.dylib -lpng -ltiff -ljpeg

lib_ext = '.so'
here  = os.path.dirname(__file__)
libiiofile= os.path.join(here, 'libiio'+lib_ext)
libiio   = CDLL(libiiofile)
del libiiofile, here, lib_ext


def read(filename):
   from numpy import array, zeros
   from ctypes import c_int, c_float, c_void_p, CDLL, POINTER, cast, byref

   iioread = libiio.iio_read_image_float_vec
   
   w=c_int()
   h=c_int()
   nch=c_int()
   
   iioread.restype = c_void_p  # it's like this
   tptr = iioread(filename,byref(w),byref(h),byref(nch))
   c_float_p = POINTER(c_float)       # define a new type of pointer
   ptr = cast(tptr, c_float_p)
   #print w,h,nch
   
   #nasty read data into array TODO IMPROVE using buffer copy
   #http://stackoverflow.com/questions/4355524/getting-data-from-ctypes-array-into-numpy
   #http://docs.scipy.org/doc/numpy/reference/generated/numpy.frombuffer.html
   data=zeros((h.value,w.value,nch.value))
   for i in range(h.value):
      for j in range(w.value):
         for c in range(nch.value):
            data[i,j,c] = ptr[(j + i*w.value)*nch.value + c]
   
   # free the memory
   iiofreemem = libiio.freemem
   iiofreemem(ptr);
   return data


def write(filename,data):
   from ctypes import CDLL, c_char_p, c_int, c_float
   from numpy.ctypeslib import ndpointer

   iiosave = libiio.iio_save_image_float_vec

   h  =data.shape[0]
   w  =data.shape[1]
   nch=1
   if (len(data.shape)>2):
      nch=data.shape[2]

   iiosave.restype = None
   iiosave.argtypes = [c_char_p, ndpointer(c_float),c_int,c_int,c_int]
   iiosave(filename, data.astype('float32'), w, h, nch)


#d = piio.read('kk.tif')
#print d.shape
#print d[:,:,0] 
#piio.write('kk2.tif',d)
