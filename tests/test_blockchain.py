import unittest
from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction

class TestBlockchain (unittest.TestCase):

    def test_init(self):
        blockchain = Blockchain()

        self.assertEqual(len(blockchain.blocks), 1)

    def test_first_transaction_in_block(self):
        blockchain = Blockchain()

        wallet1 = Wallet()

        tx1 = Transaction(0, wallet1.public_key(), None)

        # We don't care about chain's validity so we don't need to worry
        # about proof or prev block hash
        blockchain.new_block([tx1], 0, 0)

        tx1.set_block(1)

        self.assertTrue(blockchain.valid_transaction(tx1))

    def test_double_pay_transaction_fail(self):
        blockchain = Blockchain()
        wallet1 = Wallet()
        wallet2 = Wallet()
        initial_tx = Transaction(0, wallet1.public_key(), None)
        blockchain.new_block([initial_tx], 0, 0)

        tx = Transaction(wallet1.public_key(), wallet2.public_key(), initial_tx)
        blockchain.new_block([tx], 0, 0)
        self.assertTrue(blockchain.valid_transaction(tx))
        tx2 = Transaction(wallet1.public_key(), wallet2.public_key(), initial_tx)




if __name__ == '__main__':
    unittest.main()
