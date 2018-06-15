from collections import namedtuple, Sequence, OrderedDict
import re
import os
import datetime as dt
import pandas as pd

from patterns import ANZ_REGEX, REMOVE, NATWEST_REGEX

Transaction = namedtuple('Transaction', 'date bank currency amount type counter_party category exclude')

ANZ_BANK = 'ANZ'
NATWEST_BANK = 'Natwest'

CATEGORIES_FILE = 'categories'
MAX_VALUE = 20000


def read_anz(file):
    df = pd.read_csv(file, header=None)
    df.columns = ['date', 'amount', 'description']
    return df


def read_natwest(file):
    df = pd.read_csv(file)
    df.reset_index(inplace=True)
    df.columns = list(range(len(df.columns)))
    df[2] = (df[1] + ' ' + df[2]).str.replace(',', ' ').str.replace('\'', '')
    df = df[[0, 3, 2]]
    df.columns = ['date', 'amount', 'description']
    return df


def ensure_list(ll):
    if isinstance(ll, Sequence) and not isinstance(ll, str):
        return ll
    return [ll]


def parse(description, bank):
    patterns = []
    if bank == ANZ_BANK:
        patterns = ANZ_REGEX
    elif bank == NATWEST_BANK:
        patterns = NATWEST_REGEX

    for k, exp in patterns:
        for item in ensure_list(exp):
            grp = re.match(item, description)
            if grp is not None:
                return k, grp.group(1)

    print('Unable to parse', description)
    return None, None


def clean_counter_party(counter_party):
    words = counter_party.strip().replace('*', ' ').split()
    result = []
    for word in words:
        add = True
        for pattern in REMOVE:
            if re.fullmatch(pattern, word):
                add = False
                break
        if add:
            result.append(word)
    if not result:
        return counter_party
    return ' '.join(result)


def is_numeric(x):
    try:
        int(x)
        return True
    except ValueError:
        return False


class Amendments:
    def __init__(self, filename):
        self.filename = filename
        self.data = OrderedDict()
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                category = None
                for line in f.readlines():
                    line = line.strip()

                    match = re.match(r'\[([\w\s]+)\]', line)
                    if match is not None:
                        category = match.group(1)
                        self.data[category] = []
                        continue

                    parts = line.split('#')
                    if len(parts) != 4 or category is None:
                        continue

                    self.data[category].append((parts[0], parts[1], int(float(parts[3])),
                                                dt.datetime.strptime(parts[2], '%Y-%m-%d')))

    def convert(self, transactions):
        for category, values in self.data.items():
            for line in values:
                for tran in transactions:
                    if (tran.date == line[3]) and (tran.type == line[0]) and (int(tran.amount) == line[2]) and (
                        tran.counter_party == line[1]):
                        print('Updating transaction', line, 'to', category)
                        tran._replace(category=category)


class Categories:
    def __init__(self, filename):
        self.filename = filename
        self.data = OrderedDict()
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                category = None
                for line in f.readlines():
                    line = line.strip()

                    match = re.match(r'\[([\w\s]+)\]', line)
                    if match is not None:
                        category = match.group(1)
                        self.data[category] = []
                        continue

                    parts = line.split('#')
                    if len(parts) != 2 or category is None:
                        continue

                    self.data[category].append((parts[0], parts[1]))

    def save(self):
        with open(self.filename, 'w') as f:
            for category, values in self.data.items():
                f.write('[{}]\n'.format(category))
                for tt, cp in sorted(values):
                    f.write('{}#{}\n'.format(tt, cp))
                f.write('\n')

    def select(self, transaction_type, counter_party, amount):
        key = (transaction_type, counter_party)
        for category, values in self.data.items():
            if key in values:
                return category
            for tt, cp in values:
                if tt == transaction_type and cp.startswith('r'):
                    if re.fullmatch(cp[1:], counter_party):
                        print('Matched regex', cp)
                        return category
        print('No category defined for: ', transaction_type, 'c/p', counter_party, ' (amount {})'.format(amount))
        category = self._prompt()
        self.data[category].append(key)
        return category

    def _prompt(self):
        keys = list(self.data.keys())
        while True:
            print('Select: ', end='')
            for i, key in enumerate(keys):
                print('({}) {} '.format(i, key), end='')
                if i == 10:
                    print()
            print('\nOr type a new category:')
            choice = input()
            if is_numeric(choice) and 0 <= int(choice) < len(keys):
                return keys[int(choice)]
            else:
                self.data[choice] = []
                return choice


class Convert:
    def __init__(self, statement_file, bank):
        print('Running for', bank)
        print()
        self.bank = bank
        self.categories = Categories(CATEGORIES_FILE)

        if bank == 'ANZ':
            df = read_anz(statement_file)
            currency = 'AUD'
        elif bank == 'Natwest':
            df = read_natwest(statement_file)
            currency = 'GBP'
        else:
            raise ValueError('Bank not supported')

        try:
            self.transactions = df.apply(lambda x: self._convert(x, currency), axis=1)
        except KeyboardInterrupt:
            pass
        self.categories.save()

        amend = Amendments('amendments')
        amend.convert(self.transactions)

        self.transactions = pd.DataFrame([x._asdict() for x in self.transactions])

    def _convert(self, row, currency):
        date = dt.datetime.strptime(row.date, '%d/%m/%Y')
        ttype, counter_party = parse(row.description, self.bank)
        counter_party = clean_counter_party(counter_party)
        category = self.categories.select(ttype.strip(), counter_party, row.amount)
        exclude = (category == 'Exclude') or abs(row.amount) > MAX_VALUE
        return Transaction(date, self.bank, currency, row.amount, ttype, counter_party,
                           category=category, exclude=exclude)


if __name__ == '__main__':
    # conv = Convert('/Users/rjones/Downloads/ANZ (1).csv', ANZ_BANK)
    conv = Convert('/Users/rjones/Downloads/natwest.csv', NATWEST_BANK)

    conv.transactions.to_csv('out.csv')
