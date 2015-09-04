class VerifyCamelCase(object):
    
    def __init__(self, fieldName):
        
        self._fieldName = fieldName
        self._results = []
         
        self._isFirstCharacterLowerCase()
        self._isLikelySingleWord()
        self._isLikelyEntirelyAcronym()
        self._hasUnderscores()
        self._hasSpaces()
        
    def isCamelCased(self):
        
        return self._results;
        
    def _isFirstCharacterLowerCase(self):
        
        firstCharacter = self._fieldName[0]
        self._results.append(firstCharacter.islower())
        
    def _isLikelySingleWord(self):
        
        isEntirelyLowerCase = self._fieldName.islower()
        
        self._results.append(isEntirelyLowerCase and self._isShortFieldName())
    
    def _isLikelyEntirelyAcronym(self):
        
        isEntirelyUpperCase = self._fieldName.isupper()
        self._results.append(isEntirelyUpperCase and self._isVeryShortFieldName())
        
    def _hasUnderscores(self):
        
        hasUnderscores = "_" not in self._fieldName
        self._results.append(hasUnderscores)
        
    def _hasSpaces(self):
        
        hasSpaces = " " not in self._fieldName
        self._results.append(hasSpaces)
    
    def _isShortFieldName(self):
        
        return (len(self._fieldName) <= 10)
        
    def _isVeryShortFieldName(self):
    
        return (len(self._fieldName) <= 5)
        
        