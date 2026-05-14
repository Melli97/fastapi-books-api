import pytest

def test_equal_or_not_equal():
    assert 3 == 3     # Verifica che 3 sia uguale a 3 
    assert 3 != 1     # Verifica che 3 sia diverso da 1 


def test_is_instance():
    # Verifica che la stringa sia un'istanza della classe 'str'
    assert isinstance('è una stinga', str)
    # Verifica che la stringa '10' NON sia un'istanza di un intero
    assert not isinstance('10', int)

def test_boolean():
    validation = True
    assert validation is True             # Verifica identità booleana
    assert ('hello' == 'world') is False  # Il confronto restituisce False

def test_type():
    # ATTENZIONE: 'hello' is str restituisce False.
    # type(False) è <class 'bool'>, che è considerato 'True' in un assert.
    # Per verificare il tipo, usa: assert isinstance('hello', str)
    assert type('hello' is str) 
    assert type('world' is not int)   

def test_greater_and_less_than():
    assert 8 > 5      # Verifica condizione di maggiore
    assert 4 < 10     # Verifica condizione di minore

def test_list():
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, False] 
    
    assert 1 in num_list        # Verifica presenza di un elemento
    assert 7 not in num_list    # Verifica assenza di un elemento
    assert all(num_list)        # True se tutti gli elementi sono 'truthy' (diversi da 0/False)
    assert not any(any_list)    # True se nessuno degli elementi è 'truthy'



class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        # Assegnazione degli attributi all'istanza della classe
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years

@pytest.fixture
def default_employee():
    # Questa fixture crea e restituisce un'istanza di Student 
    # che può essere riutilizzata in diversi test
    return Student('marcello', 'melli', 'informatica', 3)

def test_person_initi(default_employee):
    # Verifica che il nome sia corretto. 
    # Il secondo argomento nell'assert è un messaggio personalizzato
    # che viene mostrato solo se il test fallisce.
    assert default_employee.first_name == 'marcello', 'first_name dovrebbe essere marcello'
    
    # Verifica che il cognome sia corretto
    assert default_employee.last_name == 'melli', 'last_name dovrebbe essere melli'
    
    # Verifica che il corso di laurea (major) sia corretto
    assert default_employee.major == 'informatica'
    
    # Verifica che gli anni siano corretti
    assert default_employee.years == 3