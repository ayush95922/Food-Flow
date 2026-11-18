from app.algorithms.fairness_optimizer import FairRecipient, allocate_fairly


def run_fairness(req) -> dict:
    recs = [FairRecipient(r.id, r.name, r.demand, r.capacity, r.historical_received, r.allocation_count, r.priority)
            for r in req.recipients]
    out = allocate_fairly(req.supply, recs, req.frequency_penalty, req.compare)
    out["assumptions"] = ["Cap per recipient = min(demand, capacity).",
                          f"Each past allocation is charged {req.frequency_penalty} portions of 'effective history' (assumption).",
                          "Jain's index: 1 = perfectly equal, 1/n = one recipient gets everything."]
    return out
