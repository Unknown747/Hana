# hanahanahanahana
Register : [https://hanafuda.hana.network/dashboard](https://hanafuda.hana.network/dashboard) <br><br>
enter code : ```
     KAV81W
     ```

### Requirements FarmTX
- **Node.js**: version `v14`. recomended `v16`
- **NPM**: Node Package Manager for dependencies.

### To Install 
```
git clone https://github.com/Mantodkaz/hana.git && cd hana
```
### Install dependencies 
```
npm install ethers node-fetch -y
```
### Execute farm TX
```
node hanatx.js
```

### File Usage

- **privkey.txt**: private key EVM
- **token.txt**: value refreshToken 

======================================
## Auto Claim GROW 
### Execute farm TX
```
python3 grow.py
```

### get `refreshToken` for token.txt

1. **open Console**:
   - press `F12` or `Ctrl+Shift+I` for open Developer Tools, then select tab **Console**.

2. **Allow Paste** (if necessary):
   - Insert `allow pasting` in Console if blocked.

3. **run command**:
```javascript
console.log(JSON.parse(sessionStorage.getItem(Object.keys(sessionStorage).find(k => k.startsWith('firebase:authUser:'))))?.stsTokenManager?.refreshToken);
```


## NOTE
To run script for a long period of time without being interrupted by lost terminal connections,<br>it is recommended to use **screen** or **tmux**


## Author
- MantodKaz

#### DISCAIMER !!
``I will not be held responsible for any direct or indirect damages caused by using this tool. use it only for educational purposes and you will not use it for any brutal activity.``
