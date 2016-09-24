from decimal import  *
class Solution:
   # input n: number of dice sides
   def computeRatio(self,n):
      assert n > 0
      return reduce(lambda x,y:x*float(y+1)/n, range(n),1)

a = Solution()
print a.computeRatio(10)