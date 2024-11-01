import glob

print('Challenges: '+str(len(glob.glob('ch_*.json'))))
print('Easter Eggs: '+str(len(glob.glob('egg_*.json'))))
input()