TRANSFER_FROM = 'TRANSFER_FROM'
TRANSFER_TO = 'TRANSFER_TO'
PAYMENT_TO = 'PAYMENT_TO'
CARD_PAYMENT = 'CARD_PAYMENT'
SALARY = 'SALARY'
ATM = 'ATM'
FEE = 'FEE'
INTEREST = 'INTEREST'


ANZ_REGEX = [
    (CARD_PAYMENT, [r'VISA\sDEBIT\sPURCHASE\sCARD\s\d+\s(.+)\s\w+', r'EFTPOS\s(.+\w)\s+\w+\s.+', r'REV\s(VISA)\sDEBIT\sPURCHASE']),
    (TRANSFER_TO,  [r'.*PAYMENT\sTRANSFER\s\d+\sTO\s(.+)', r'ANZ\sINTERNET\sBANKING\sFUNDS\sTFER\sTRANSFER\s\d+.+TO\s+(.+)']),
    (TRANSFER_FROM, [r'TRANSFER\sFROM\s(\w+(?:\s\w+)*)', r'ANZ\s(?:INTERNET\s|M-)BANKING\sFUNDS\sTFER\s+(?:.*FROM\s+)?(.+)', r'PAYMENT\sFROM\s([\s\w]+)']),
    (PAYMENT_TO, [r'.*BANKING\sBPAY\s(\w+).*', r'PAYMENT\sTO\s(.+)\s.*']),
    (SALARY, r'PAY.SALARY\sFROM\s((?:\w+\s)?(?:\w+\s)?(?:\w+)?).*'),
    (ATM, [r'.*(ATM\s).*', r'(CARD\sENTRY)\sAT\s.*']),
    (FEE, r'.*ACCOUNT SERVICING (FEE).*'),
    (INTEREST, r'.*(INTEREST).*')
]

NATWEST_REGEX = [
    (CARD_PAYMENT, [r'POS\s(.+)']),
    (TRANSFER_TO,  [r'DPC\s(.+)']),
    (TRANSFER_FROM, []),
    (PAYMENT_TO, [r'D\/D\s(.*)', r'DPC']),
    (SALARY, []),
    (ATM, [r'C\/L\s(.*)']),
    (FEE, r'CHG\s(.*)'),
    (INTEREST, r'INT\s(.*)')
]

REMOVE = [
    r'[\d\.-]+(?:[AP]M)?',
    r'(MON|TUE|WED|THU|FRI|SAT|SUN)',
    r'(GBP|USD|AUD)',
    r'(T1|#?\+?\d[A-Z\d]+|[A-Z\d]+\d)',
    r'(INC|O\/S|VRATE|AU)',
    r'(FGN|PUR|FEE)',
    r'SYDNEY'
]