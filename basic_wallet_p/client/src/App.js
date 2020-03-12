import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
    const server = 'http://localhost:5000'
    const [lastUsername, setLastUsername] = useState('melqui')
    const [username, setUsername] = useState('melqui')
    const [balance, setBalance] = useState(0)
    const [isMining, setIsMining] = useState(false)
    const [transactions, setTransactions] = useState([])
    const [recipient, setRecipient] = useState('')
    const [amount, setAmount] = useState(0)
    const [lastBlock, setLastBlock] = useState(null)


    useEffect(() => {
        axios.post(`${server}/user/balance`, { 'username': lastUsername }).then(res => {
            console.log('/user/balance', res.data.balance)
            setBalance(res.data.balance)
        }).catch(err => console.error(err));
        axios.post(`${server}/user/transactions`, { 'username': lastUsername }).then(res => {
            console.log('/user/transactions', res.data.transactions)
            setTransactions(res.data.transactions)
        }).catch(err => console.error(err));
        /* axios.get(`${server}/last_block`).then(res => {
            console.log('/last_block', res.data.last_block)
            setLastBlock(res.data.last_block)
        }).catch(err => console.error(err)); */
    }, [])

    const onChangeUsername = (e) => {
        const { value } = e.target;
        setUsername(value)
    }

    const onChangeRecipient = (e) => {
        const { value } = e.target;
        setRecipient(value)
    }

    const onChangeAmount = (e) => {
        const { value } = e.target;
        setAmount(value)
    }

    const onChangeUsernameSubmit = (e) => {
        e.preventDefault();
        axios.post(`${server}/user/change`, { lastUsername, username }).then(res => {
            console.log('/user/change', res)
            if (res.data.success) {
                setLastUsername(username)
            }
        }).catch(err => console.error(err));
    }

    const onSubmitSendTransaction = (e) => {
        e.preventDefault();
        axios.post(`${server}/transaction/new`, {
            'sender': lastUsername,
            'recipient': recipient,
            'amount': amount,
        }).then(res => {
            console.log('/transaction/new', res)
            setRecipient('')
            setAmount(0)
        }).catch(err => console.error(err));
    }

    const onClickStartMine = (e) => {
        if (!isMining) {
            setIsMining(true)
            axios.post(`${server}/mine`, {
                // 'block': lastBlock,
                'username': lastUsername
            }).then(res => {
                console.log('/mine', res.data)
                const myTransactions = res.data.transactions.filter(t => t.sender === lastUsername || t.recipient === lastUsername)
                setTransactions(prevState => [
                    ...prevState,
                    ...myTransactions
                ]);
                console.log(myTransactions, myTransactions.reduce((total, t) => {
                    if (t.sender === lastUsername) {
                        total -= t.amount
                    } else if (t.recipient === lastUsername) {
                        total += t.amount
                    }
                    return total
                }, 0))
                setBalance(prevState => prevState + myTransactions.reduce((total, t) => {
                    if (t.sender === lastUsername) {
                        total -= t.amount
                    } else if (t.recipient === lastUsername) {
                        total += t.amount
                    }
                    return total
                }, 0));
                
            }).catch(err => {
                console.error(err)
            }).finally(e => {
                setIsMining(false)
            });
        }
    }

    return (
        <div className="App">
            <h2>{lastUsername}'s balance: {balance} Coins</h2>
            <form onSubmit={onChangeUsernameSubmit}>
                <label htmlFor="username">User name:</label>
                <input id="username" type="text" value={username} onChange={onChangeUsername} />
                <button>Change now</button>
            </form>
            {
                !isMining ? <>
                    <h2>Start Mining</h2>
                    <button onClick={onClickStartMine}>Start Mining</button>
                </> : <>
                        <h2>Mining...</h2>
                    </>
            }

            <br />
            <h2>Send coins to someone else!</h2>
            <form onSubmit={onSubmitSendTransaction}>
                <label htmlFor="recipient">Recipient:</label>
                <input id="recipient" type="text" value={recipient} onChange={onChangeRecipient} required />
                <label htmlFor="amount">Amount:</label>
                <input id="amount" type="number" value={amount} onChange={onChangeAmount} step="0.01" min="0" max={balance} required />
                {
                    amount > 0 && amount <= balance && recipient ?
                        <button>Send {amount} coins to {recipient}</button>
                        : null
                }
            </form>
            <h2>All Transactions so far</h2>
            {
                transactions.map((t, i) => <div key={i} className="transaction">
                    <p>Sender: {t.sender}</p>
                    <p>Recipient: {t.recipient}</p>
                    <p>Amount: {t.amount}</p>
                </div>)
            }
        </div>
    );
}

export default App;
