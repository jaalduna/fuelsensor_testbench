import pickle

obj0 = bytearray({0,1,2})
with open('objs.pkl', 'w') as f:  # Python 3: open(..., 'wb')
    pickle.dump([obj0, obj1, obj2], f)