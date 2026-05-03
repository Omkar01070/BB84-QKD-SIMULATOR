
# app.py — BB84 Web Simulator (NO CASCADE, CONSERVATIVE EVE DETECTION)

import joblib
eve_model = joblib.load("eve_detector.pkl")


from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import uvicorn
import os
import math
import numpy as np
import json
import asyncio
import random

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import Aer
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    amplitude_damping_error,
    phase_damping_error,
    pauli_error,
)



# APP SETUP


app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

backend = Aer.get_backend("aer_simulator")

# QUANTUM RANDOM STRING

def RandomStringG(str_len: int, batch_size: int = 20) -> str:
    if str_len <= 0:
        return ""
    out = ""
    for start in range(0, str_len, batch_size):
        n = min(batch_size, str_len - start)
        qc = QuantumCircuit(n, n)
        qc.h(range(n))
        qc.measure(range(n), range(n))
        tqc = transpile(qc, backend, optimization_level=0)
        bits = list(backend.run(tqc, shots=1).result().get_counts().keys())[0]
        out += bits[::-1]
    return out



def encode_ascii_shift(message: str, alice_bits: str) -> str:
    return "".join(
        chr((ord(m) + (10 + ord(k)) % 256) % 256)
        for m, k in zip(message, alice_bits)
    )


def decode_ascii_shift(cipher: str, bob_bits: str) -> str:
    return "".join(
        chr((ord(c) - (10 + ord(k)) % 256) % 256)
        for c, k in zip(cipher, bob_bits)
    )


import random



import random

# def cascade_protocol(A_key, B_key, initial_block_size, num_rounds):

#     if len(A_key) != len(B_key):
#         raise ValueError("Keys must be of the same length.")

#     corrected_B = list(B_key)
#     n = len(A_key)
#     total_flips = 0
#     block_size = initial_block_size
#     correction_log = []

#     parity_checks = 0   # ⭐ NEW: count parity computations

#     print(f"\n Starting Cascade Protocol on {n}-bit key")
#     print(f"Initial block size: {block_size}, Total rounds: {num_rounds}\n")

#     for round_num in range(1, num_rounds + 1):
#         print(f"=== Round {round_num} | Block size = {block_size} ===")
#         round_flips = 0

#         indices = list(range(0, n, block_size))
#         random.shuffle(indices)

#         for start in indices:
#             end = min(start + block_size, n)
#             block_A = A_key[start:end]
#             block_B = corrected_B[start:end]

#             # ⭐ Parity of full block
#             parity_A = sum(int(bit) for bit in block_A) % 2
#             parity_B = sum(int(bit) for bit in block_B) % 2
#             parity_checks += 1

#             if parity_A != parity_B:
#                 left, right = 0, len(block_A) - 1
#                 while left < right:
#                     mid = (left + right) // 2

#                     parity_A_left = sum(int(bit) for bit in block_A[left:mid+1]) % 2
#                     parity_B_left = sum(int(corrected_B[start + i]) for i in range(left, mid + 1)) % 2
#                     parity_checks += 1  # ⭐ each binary search step leaks 2 parities

#                     if parity_A_left != parity_B_left:
#                         right = mid
#                     else:
#                         left = mid + 1

#                 error_index = start + left
#                 corrected_B[error_index] = '0' if corrected_B[error_index] == '1' else '1'
#                 total_flips += 1
#                 round_flips += 1

#         correction_log.append(round_flips)
#         print(f" Round {round_num} complete — {round_flips} bit(s) corrected.\n")

#         block_size = min(block_size + 1, n)

#     corrected_B = ''.join(corrected_B)

#     print(" Cascade complete.")
#     print(f"Total corrections made: {total_flips}")
#     print(f"Total parity checks (information leaked): {parity_checks}")
#     print(f"Final parity match: {'coorectedB key matched' if corrected_B == A_key else 'correctedB not completely matched'}")

#     return corrected_B, total_flips, correction_log, parity_checks

import random

def cascade_protocol(A_key, B_key, initial_block_size, num_rounds):

    if len(A_key) != len(B_key):
        raise ValueError("Keys must be of the same length.")

    corrected_B = list(B_key)
    n = len(A_key)
    total_flips = 0
    correction_log = []
    parity_checks = 0
    round_blocks = []

    print(f"\nStarting Full CASCADE on {n}-bit key")

    block_size = initial_block_size

    for round_num in range(num_rounds):

        print(f"\n=== Round {round_num + 1} | Block size = {block_size} ===")
        round_flips = 0

        indices = list(range(0, n, block_size))
        random.shuffle(indices)

        blocks = [(start, min(start + block_size, n)) for start in indices]
        round_blocks.append(blocks)

        for start, end in blocks:
            parity_A = sum(int(A_key[i]) for i in range(start, end)) % 2
            parity_B = sum(int(corrected_B[i]) for i in range(start, end)) % 2
            parity_checks += 1

            if parity_A != parity_B:
                error_index, parity_checks = binary_search_error(
                    A_key, corrected_B, start, end, parity_checks
                )

                corrected_B[error_index] = '0' if corrected_B[error_index] == '1' else '1'
                total_flips += 1
                round_flips += 1

                parity_checks = cascade_backtrack(
                    A_key, corrected_B, error_index, round_blocks, round_num, parity_checks
                )

        correction_log.append(round_flips)
        print(f"Round {round_num+1} corrected {round_flips} bits.")

        block_size = min(block_size * 2, n)

    corrected_B = ''.join(corrected_B)

    print("\nCASCADE complete.")
    print(f"Total corrections: {total_flips}")
    print(f"Parity bits leaked: {parity_checks}")
    # print("Final match:", corrected_B == A_key)

    return corrected_B, total_flips, correction_log, parity_checks



def binary_search_error(A_key, B_key, start, end, parity_checks):
    left, right = start, end - 1

    while left < right:
        mid = (left + right) // 2

        parity_A = sum(int(A_key[i]) for i in range(left, mid + 1)) % 2
        parity_B = sum(int(B_key[i]) for i in range(left, mid + 1)) % 2
        parity_checks += 1

        if parity_A != parity_B:
            right = mid
        else:
            left = mid + 1

    return left, parity_checks



def cascade_backtrack(A_key, B_key, error_index, round_blocks, current_round, parity_checks):

    for r in range(current_round):
        for start, end in round_blocks[r]:
            if start <= error_index < end:

                parity_A = sum(int(A_key[i]) for i in range(start, end)) % 2
                parity_B = sum(int(B_key[i]) for i in range(start, end)) % 2
                parity_checks += 1

                if parity_A != parity_B:
                    new_error, parity_checks = binary_search_error(
                        A_key, B_key, start, end, parity_checks
                    )
                    B_key[new_error] = '0' if B_key[new_error] == '1' else '1'

    return parity_checks


import math

def eve_information_bits(Q, raw_key_length):
    """
    Q : QBER (0 <= Q <= 1)
    raw_key_length : number of bits after error correction (n)

    Returns:
        bits_to_remove : number of bits privacy amplification should remove
    """

    if not (0 <= Q <= 1):
        raise ValueError("QBER must be between 0 and 1.")

    # Handle edge cases to avoid log(0)
    if Q == 0 or Q == 1:
        hQ = 0.0
    else:
        hQ = -Q * math.log2(Q) - (1 - Q) * math.log2(1 - Q)

    bits_to_remove = raw_key_length * hQ
    return math.ceil(bits_to_remove)  # round up for safety


# import hashlib

# def privacy_amplification(key_bits, compression_ratio=0.7):
#     """
#     key_bits: binary string
#     compression_ratio: fraction of bits kept
#     """

#     # Convert bitstring to bytes
#     key_bytes = int(key_bits, 2).to_bytes((len(key_bits) + 7) // 8, 'big')

#     # Hash
#     digest = hashlib.sha256(key_bytes).digest()

#     # Convert back to bitstring
#     digest_bits = bin(int.from_bytes(digest, 'big'))[2:].zfill(256)

#     # Keep only part of hash
#     final_len = int(len(key_bits) * compression_ratio)
#     return digest_bits[:final_len]

import secrets

def toeplitz_privacy_amplification(key_bits, bits_to_remove,seed):
    """
    key_bits: string of '0' and '1'
    bits_to_remove: number of bits to remove due to Eve's information
    returns: final secret key bitstring
    """

    n = len(key_bits)
    m = n - bits_to_remove  # final key length

    if m <= 0:
        raise ValueError("Compression too large. No key remains.")

    # Convert key to list of integers (0/1)
    key = [int(b) for b in key_bits]

    # Generate Toeplitz defining vector (n + m - 1 random bits)
    ########toeplitz_seed = [secrets.randbits(1) for _ in range(n + m - 1)]

    # Compute output bits
    final_key = []

    for i in range(m):
        # Each row of Toeplitz is shifted version of seed
        xor_sum = 0
        for j in range(n):
            xor_sum ^= seed[i + j] & key[j]
        final_key.append(str(xor_sum))

    return ''.join(final_key)



def run_bb84(
    initial_key_length,
    segment_size,
    px, pz, pi,
    amp_flag, pol_flag, phase_flag, depol_flag,
    amp_prob, phase_prob, depol_prob,
):

    num_qbits = 20
    L = max(0, initial_key_length)

    #  Alice raw key 
    blocks = [num_qbits] * (L // num_qbits)
    if L % num_qbits:
        blocks.append(L % num_qbits)
    key_A = "".join(RandomStringG(b) for b in blocks)

    #- Noise Model
    noise_model = NoiseModel()

    amp = amplitude_damping_error(amp_prob if amp_flag else 0)
    phs = phase_damping_error(phase_prob if phase_flag else 0)
    dpl = depolarizing_error(depol_prob if depol_flag else 0, 1)

    if not pol_flag:
        pol = pauli_error([("I", 1.0)])
        pxn = pzn = 0
        pin = 1
    else:
        tot = px + pz + pi
        pxn = px / tot if tot else 0
        pzn = pz / tot if tot else 0
        pin = pi / tot if tot else 1
        ent = []
        if pxn > 0: ent.append(("X", pxn))
        if pzn > 0: ent.append(("Z", pzn))
        if pin > 0: ent.append(("I", pin))
        pol = pauli_error(ent)

    channel = amp.compose(phs).compose(dpl).compose(pol)
    noise_model.add_all_qubit_quantum_error(channel,
        ["h", "x", "id", "u1", "u2", "u3"]
    )

    num_segments = math.ceil(L / segment_size)
    bases_A = RandomStringG(num_segments)
    bases_B = RandomStringG(num_segments)

    alice_final = ""
    bob_final = ""

    segment_qbers = []
    total_m = 0
    total_cmp = 0
    matched_segments = 0

    
    for si in range(num_segments):

        ss = si * segment_size
        ee = min(ss + segment_size, L)

        segA = key_A[ss:ee]
        ab = int(bases_A[si])
        bb = int(bases_B[si])

        if ab != bb:
            segment_qbers.append(0.0)
            continue

        matched_segments += 1
        bob_seg = ""

        for bs in range(ss, ee, num_qbits):
            be = min(bs + num_qbits, ee)
            block = segA[bs-ss: be-ss]

            q = QuantumRegister(len(block))
            c = ClassicalRegister(len(block))
            qc = QuantumCircuit(q, c)

            for i, b in enumerate(block):
                if b == "1":
                    qc.x(q[i])
                if ab == 1:
                    qc.h(q[i])

            for i in range(len(block)):
                if bb == 1:
                    qc.h(q[i])
                qc.measure(q[i], c[i])

            tqc = transpile(qc, backend, optimization_level=0)
            out = list(backend.run(tqc, noise_model=noise_model, shots=1)
                       .result().get_counts().keys())[0]
            bob_seg += out[::-1]
        compare_len = int(len(segA) * 0.30)
        mism = sum(1 for i in range(compare_len) if segA[i] != bob_seg[i])

        q = mism / compare_len if compare_len else 0
        total_m += mism
        total_cmp += compare_len
        segment_qbers.append(round(q * 100, 2))

        # Keep last 70% 
        alice_final += segA[compare_len:]
        bob_final += bob_seg[compare_len:]

    
    global_qber = (total_m / total_cmp) * 100 if total_cmp else 0
    nz = [x for x in segment_qbers if x > 0]
    avg_q = f"{np.mean(nz):.2f}%" if nz else "0.00%"

    # CONSERVATIVE EAVESDROPPER DETECTION

    # if global_qber >= thetah:
    #     eve_detected = True
    # elif global_qber <= thetal:
    #     eve_detected = False
    # else:
    #     # Compute probabilistic detection
    #     ratio = (global_qber - thetal) / (thetah - thetal)
    #     P_attack = gamma_h * ratio + gamma_l * (1 - ratio)
    #     eve_detected = (random.random() < P_attack)

    cascade_enabled = True  # hardcoded ON for now

    if cascade_enabled and len(alice_final) > 0:
        corrected_B, total_fixed, round_log, parity_checks = cascade_protocol(alice_final,bob_final,initial_block_size=5,num_rounds=2)
    else:
        corrected_B = bob_final
        total_fixed = 0
        round_log = []

    eve_bits=eve_information_bits(global_qber/100,len(corrected_B)) 
    
    bits_to_remove= eve_bits +  parity_checks
    
    # Privacy Amplification 
    # Generate shared Toeplitz seed

    if bits_to_remove >= len(corrected_B):
        alice_pa_key = ""
        bob_pa_key = ""
       
    else:      
            n = len(corrected_B)
            m = n - bits_to_remove
            toeplitz_seed = [secrets.randbits(1) for _ in range(n + m - 1)]

            if len(alice_final) > 0:
                alice_pa_key = toeplitz_privacy_amplification(corrected_B, bits_to_remove, toeplitz_seed)
                bob_pa_key   = toeplitz_privacy_amplification(corrected_B, bits_to_remove, toeplitz_seed)

            else:
                alice_pa_key = ""
                bob_pa_key   = ""
    
    import pandas as pd
    
    # QBER variance (for ML features)
    qber_var = np.var(segment_qbers) if len(segment_qbers) > 0 else 0.0

    features = pd.DataFrame([{
        "global_qber": round(global_qber, 2),
        "qber_variance": qber_var,
        "matched_segments": matched_segments,
        "amp_prob": amp_prob,
        "phase_prob": phase_prob,
        "depol_prob": depol_prob,
        "pauli_x": pxn,
        "pauli_z": pzn
    }])

    features = features.drop("global_qber", axis=1)
    eve_prob = eve_model.predict_proba(features)[0][1]

    eve_detected_ml = eve_prob > 0.5

    #
    skr = len(alice_pa_key) / initial_key_length if initial_key_length else 0
    print("total bits to be removed ",bits_to_remove)
    
    print("bits leaked (holevo bound)",eve_bits)
    print(qc)
    return {
        "Key_Alice_Raw": key_A,
        "Alice_Final_Key": alice_final,

        "Bob_Final_Key": corrected_B,
        "Bob_Key_Before_Cascade": bob_final,
        "Total_Cascade_Fixes": total_fixed,
        "Cascade_Round_Log": round_log,

        "Segment_QBERs": segment_qbers,
        "Segment_QBERs_json": json.dumps(segment_qbers),
        "QBER_Global": round(global_qber, 2),
        "Average_Segment_QBER": avg_q,
        "Matched_Segments": matched_segments,

        # "Eve_Detected": eve_detected,
        "Eve_Detected_ML": eve_detected_ml,
        "Eve_Probability": round(eve_prob * 100, 2),
        #
        "Alice_PA_Key": alice_pa_key,
        "Bob_PA_Key": bob_pa_key,
        #
        "Pauli_Probabilities": {
            "X": round(pxn * 100, 2),
            "Z": round(pzn * 100, 2),
            "I": round(pin * 100, 2),
        },

        #
        "Final_Key_Length_PA": len(alice_pa_key),
        "Secret_Key_Rate": round(skr, 4),
        "SKR_json": json.dumps([skr]),
    }

# ROUTES


@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    defaults = {
        "initial_key_length": 128,
        "segment_size": 100,
        "pauli_p_x": 0.0,
        "pauli_p_z": 0.0,
        "pauli_p_i": 1.0,
        # "theta_qber_0": 8.0,
        # "theta_qber_h": 12.0,
        # "theta_qber_l": 3.0,
        # "gamma_h": 0.25,
        # "gamma_l": 0.25,
        "amp_flag": False,
        "pol_flag": False,
        "phase_flag": False,
        "depol_flag": False,
    }
    return templates.TemplateResponse("index2.html", {
        "request": request,
        "result": None,
        "defaults": defaults
    })


@app.post("/", response_class=HTMLResponse)
async def post_form(
    request: Request,
    initial_key_length: int = Form(...),
    segment_size: int = Form(...),

    pauli_px: float = Form(0.0),
    pauli_pz: float = Form(0.0),
    pauli_pi: float = Form(0.0),

    amp_prob: float = Form(0.0),
    phase_prob: float = Form(0.0),
    depol_prob: float = Form(0.0),

    amp_flag: str | None = Form(None),
    pol_flag: str | None = Form(None),
    phase_flag: str | None = Form(None),
    depol_flag: str | None = Form(None),

    # theta_qber_0: float = Form(...),
    # theta_qber_h: float = Form(...),
    # theta_qber_l: float = Form(...),
    # gamma_h: float = Form(...),
    # gamma_l: float = Form(...),

    send_paragraph: str = Form(""),
):

    res = await asyncio.to_thread(
        run_bb84,
        initial_key_length * 40,
        segment_size,
        pauli_px, pauli_pz, pauli_pi,
        # theta_qber_0, theta_qber_h, theta_qber_l,
        # gamma_h, gamma_l,
        amp_flag == "on",
        pol_flag == "on",
        phase_flag == "on",
        depol_flag == "on",
        amp_prob, phase_prob, depol_prob
    )

    # Encode message 
    # Encode message (ONLY ONCE, unchanged)
    #1 encoded = encode_ascii_shift(send_paragraph, res["Alice_Final_Key"])
    encoded = encode_ascii_shift(send_paragraph, res["Alice_PA_Key"])
    
    #  Decode using Bob key BEFORE CASCADE 
    decoded_before = decode_ascii_shift(encoded, res["Bob_Key_Before_Cascade"])

    # Decode using Bob key AFTER CASCADE
    #1 decoded_after = decode_ascii_shift(encoded, res["Bob_Final_Key"])
    decoded_after = decode_ascii_shift(encoded, res["Bob_PA_Key"])

    res["Encoded"] = encoded
    res["Decoded_Before_Cascade"] = decoded_before
    res["Decoded_After_Cascade_PA"] = decoded_after


    # Save form values
    res["_form_values"] = {
        "initial_key_length": initial_key_length,
        "segment_size": segment_size,
        "pauli_p_x": pauli_px,
        "pauli_p_z": pauli_pz,
        "pauli_p_i": pauli_pi,
        # "theta_qber_0": theta_qber_0,
        # "theta_qber_h": theta_qber_h,
        # "theta_qber_l": theta_qber_l,
        # "gamma_h": gamma_h,
        # "gamma_l": gamma_l,
        "amp_flag": amp_flag == "on",
        "pol_flag": pol_flag == "on",
        "phase_flag": phase_flag == "on",
        "depol_flag": depol_flag == "on",
        "amp_prob": amp_prob,
        "phase_prob": phase_prob,
        "depol_prob": depol_prob,
        "send_paragraph": send_paragraph,
    }

    return templates.TemplateResponse("index2.html", {
        "request": request,
        "result": res,
        "defaults": None
    })


# =============================================================
# SERVER
# =============================================================

if __name__ == "__main__":
    uvicorn.run("app2:app", host="127.0.0.1", port=5500, reload=True)
