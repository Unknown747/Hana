const { JsonRpcProvider, Wallet, Contract, parseEther } = require("ethers");
const fetch = (...args) => import("node-fetch").then(({ default: fetch }) => fetch(...args));
const fs = require("fs");

const contractAddress = "0xc5bf05cd32a14bffb705fb37a9d218895187376c";
const contractABI = [
    {
        "inputs": [],
        "name": "depositETH",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
];
const provider = new JsonRpcProvider("https://mainnet.base.org");

let refreshToken;
let bearerToken;
let wallet;

async function initializeWallet() {
    if (fs.existsSync("privkey.txt")) {
        const privateKey = fs.readFileSync("privkey.txt", "utf-8").trim();
        wallet = new Wallet(privateKey, provider);
    } else {
        console.error("File privkey.txt tidak ditemukan.");
        process.exit(1);
    }
}

async function initializeTokens() {
    if (fs.existsSync("token.txt")) {
        refreshToken = fs.readFileSync("token.txt", "utf-8").trim();
    } else {
        console.error("File token.txt tidak ditemukan.");
        process.exit(1);
    }

    if (fs.existsSync("bearer.txt")) {
        bearerToken = fs.readFileSync("bearer.txt", "utf-8").trim();
    } else {
        console.log("Memperbarui token Bearer...");
        await refreshBearerToken();
    }
}

async function refreshBearerToken() {
    const url = "ht" + "tps://" + "secure" + "token.goog" + "leapis." + "com/v1/t" + "oken" + "?k" + "ey=AIz" + "aSy" + "Dip" + "zN" + "0VRf" + "TPnM" + "GhQ" + "5PS" + "zO27" + "Cxm3" + "Doh" + "JGY";
    const body = `grant_type=refresh_token&refresh_token=${refreshToken}`;

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://hanafuda.hana.network/",
                "Referer": "https://hanafuda.hana.network/",
                "Referrer-Policy": "strict-origin-when-cross-origin"
            },
            body
        });
        
        const data = await response.json();
        if (data.access_token) {
            bearerToken = data.access_token;
            fs.writeFileSync("bearer.txt", bearerToken);
            return true;
        } else {
            console.error("Gagal memperbarui Sesi:", data);
            return false;
        }
    } catch (error) {
        console.error("Error saat memperbarui Sesi:", error);
        return false;
    }
}

async function getTransactionReceiptWithRetry(txHash) {
    while (true) {
        try {
            const receipt = await provider.getTransactionReceipt(txHash);
            if (receipt) {
                return receipt;
            }
            await new Promise(resolve => setTimeout(resolve, 3000)); 
        } catch (error) {
            if (error.error && error.error.message.includes("over rate limit")) {
                console.warn("Over rate limit TX detected. Retrying...");
                await new Promise(resolve => setTimeout(resolve, 5000));
            } else {
                throw error;
            }
        }
    }
}

async function executeTransactionAndSubmit(nonce) {
    const amountInEth = "0.00000042";
    const amountInWei = parseEther(amountInEth);
    const contract = new Contract(contractAddress, contractABI, wallet);

    while (true) {
        try {
            const tx = await contract.depositETH({ value: amountInWei, gasLimit: 100000, nonce });
            const receipt = await getTransactionReceiptWithRetry(tx.hash); 
            console.log("TX:", tx.hash);
            
            const success = await submitTransaction(tx.hash);
            return success;
        } catch (error) {
            if (error.code === 'UNKNOWN_ERROR' && error.error && error.error.message.includes("over rate limit")) {
                console.warn("Over rate limit. Menunggu sebelum mencoba ulang...");
                await new Promise(resolve => setTimeout(resolve, 5000)); 
            } else {
                console.error("Error transaksi:", error);
                return false;
            }
        }
    }
}

async function submitTransaction(txHash) {
    const url = "ht" + "t" + "ps:/" + "/ha" + "n" + "afu" + "da-bac" + "ke" + "nd-ap" + "p-" + "5" + "2047" + "8841" + "3" + "86" + ".us-cen" + "tral1" + ".run" + ".app/" + "gra" + "phql";
    const headers = {
        "accept": "application/graphql-response+json, application/json",
        "content-type": "application/json",
        "authorization": `Bearer ${bearerToken}`,
        "priority": "u=1, i",
        "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://hanafuda.hana.network/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    };

    const body = JSON.stringify({
        query: "mutation SyncEthereumTx($chainId: Int!, $txHash: String!) {\n  syncEthereumTx(chainId: $chainId, txHash: $txHash)\n}",
        variables: { chainId: 8453, txHash },
        operationName: "SyncEthereumTx"
    });

    try {
        const response = await fetch(url, { method: "POST", headers, body });
        const result = await response.json();
        console.log("output:", result);

        if (response.status !== 200 || (result.errors && result.errors[0].message === "Unauthorized")) {
            console.error("Unauthorized. Memperbarui sesi...");
            const tokenRefreshed = await refreshBearerToken(); // memperbaiki nama fungsi
            return tokenRefreshed ? await submitTransaction(txHash) : false;
        }

        if (result.errors && result.errors[0].message.includes("Transaction not found")) {
            console.warn("Transaction not found. mencoba ulang...");
            await new Promise(resolve => setTimeout(resolve, 5000)); 
            return await submitTransaction(txHash);
        }
        return true;
    } catch (error) {
        console.error("Gagal submit txHash:", error);
        return false;
    }
}

async function startParallelLoop(parallelCount) {
    let nonce = await provider.getTransactionCount(wallet.address, "latest");

    while (true) {
        const promises = [];
        for (let i = 0; i < parallelCount; i++) {
            promises.push(executeTransactionAndSubmit(nonce));
            nonce++;
        }

        const results = await Promise.all(promises);
        console.log("Waiting...");
        await new Promise(resolve => setTimeout(resolve, 4000)); //turu 4 detik
    }
}

initializeWallet().then(initializeTokens).then(() => startParallelLoop(3)); //paralel default = 3
