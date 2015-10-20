class VerifyCamelCase(object):
    
    def __init__(self, field_name):
        
        self._field_name = field_name
        
    def is_camel_cased(self):
        
        is_camel_cased = True
        
        if self._has_underscores() or self._has_spaces():
            is_camel_cased = False

        elif self._is_first_character_lower_case():
            is_camel_cased = self._is_mixed_case() or self._is_likely_single_word()
            
        else:
            
            if self._is_mixed_case():
                is_camel_cased = self._is_likely_starting_with_acronym()

            # Its entirely upper case
            else:
                is_camel_cased = self._is_likely_field_is_entirely_acronym()
        
        return is_camel_cased

    def _has_underscores(self):
        
        return "_" in self._field_name
        
    def _has_spaces(self):
        
        return " " in self._field_name
        
    def _is_first_character_lower_case(self):
        
        return self._field_name[0].islower()
        
    def _is_mixed_case(self):
        
        return (not self._field_name.islower()) and (not self._field_name.isupper())
    
    def _is_likely_single_word(self):

        return len(self._field_name) <= 10
    
    def _is_likely_starting_with_acronym(self):
        return self._field_name[1].isupper()
        
    def _is_likely_field_is_entirely_acronym(self):
        return len(self._field_name) <= 4
