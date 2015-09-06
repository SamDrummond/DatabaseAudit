class VerifyCamelCase(object):
    
    def __init__(self, fieldName):
        
        self._fieldName = fieldName
        
    def isCamelCased(self):
        
        isCamelCased = True
        
        if self._hasUnderscores() or self._hasSpaces():
            isCamelCased = False
        elif self._isFirstCharacterLowerCase():
            
            isCamelCased =  self._isMixedCase() or self._isLikelyASingleWord()
            
        else:
            
            if self._isMixedCase():
                
                isCamelCased = self._isLikelyStartingWithAcronym()
            
            else: #its entirely upper case

                isCamelCased = self._isLikelyFieldIsEntirelyAcronym()
        
        return isCamelCased
        
    def _hasUnderscores(self):
        
        return ("_" in self._fieldName)
        
    def _hasSpaces(self):
        
        return (" " in self._fieldName)
        
    def _isFirstCharacterLowerCase(self):
        
        return self._fieldName[0].islower()
        
    def _isMixedCase(self):
        
        return (not self._fieldName.islower()) and (not self._fieldName.isupper())
    
    def _isLikelyASingleWord(self):
        
        return (len(self._fieldName) <= 10)
    
    def _isLikelyStartingWithAcronym(self):
        return self._fieldName[1].isupper() 
        
    def _isLikelyFieldIsEntirelyAcronym(self):
        return (len(self._fieldName) <= 4)
    
        
        