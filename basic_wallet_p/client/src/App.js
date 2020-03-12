import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
    const server = 'http://localhost:5000'
    const [lastUsername, setLastUsername] = useState('melqui')
    const [username, setUsername] = useState('melqui')
    const [balance, setBalance] = useState(0)

    useEffect(() => {
        axios.post(`${server}/getUserBalance`, { 'username': lastUsername }).then(res => {
            console.log('getUserBalance', res)
            setBalance(res.data.balance)
        }).catch(err => console.error(err));
    }, [])

    const onChangeUsername = (e) => {
        const { value } = e.target;
        setUsername(value)
    }

    const onChangeUsernameSubmit = (e) => {
        e.preventDefault();
        axios.post(`${server}/changeUsername`, { lastUsername, username }).then(res => {
            console.log(res)
            setLastUsername(username)
        }).catch(err => console.error(err));
    }

    return (
        <div className="App">
            <h3>{lastUsername}'s balance: {balance} Coins</h3>
            <form onSubmit={onChangeUsernameSubmit}>
                <label htmlFor="username">User name:</label>
                <input id="username" type="text" value={username} onChange={onChangeUsername} />
                <button>Submit</button>
            </form>
        </div>
    );
}

export default App;
