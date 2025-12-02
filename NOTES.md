# Implementation Notes

**Candidate Name:** [Mouheb Baalouch]  
**Date:** [02/12/2025]  
**Time Spent:** [2]

---

## 📝 Summary

Brief overview of what you implemented and your overall approach.

---

ingest_data():

  Consolidate multiple batches into a single DataFrame.

  Remove duplicates based on timestamp + sensor + value.

  Remove rows with missing value to avoid propagating empty readings.

  Standardize quality flags (GOOD, BAD, UNCERTAIN) for consistency.

  Remove rows with quality = BAD.

  Normalize units (if necessary) and create derived columns like is_outlier for optional preprocessing.

  Sort all readings by timestamp to maintain chronological order.

detect_anomalies():
  Filter data for the chosen sensor.

  Convert value to numeric and drop any remaining NaNs.

  Implement z-score method:

  Calculate mean and standard deviation of the sensor readings.

  Compute z-score for each reading.

  Flag readings as anomalies if abs(z-score) > threshold.

  Handle edge cases:

  Avoid division by zero if standard deviation is zero.

  Safely handle small datasets.

  Merge results back with original data so all sensors remain.
## ✅ Completed

List what you successfully implemented:

- [ ] `ingest_data()` - basic functionality✅
- [ ] `ingest_data()` - deduplication✅
- [ ] `ingest_data()` - sorting✅
- [ ] `ingest_data()` - validation✅
- [ ] `detect_anomalies()` - zscore method✅
- [ ] `detect_anomalies()` - additional methods (iqr/rolling)✅
- [ ] `summarize_metrics()` - basic statistics
- [ ] `summarize_metrics()` - quality metrics
- [ ] `summarize_metrics()` - time windowing
- [ ] Additional tests beyond exposed tests

---

## 🤔 Assumptions & Design Decisions

Document key assumptions and why you made certain design choices.

### Data Ingestion
- **Assumption 1:** I assumed that all sensor values are numerical
  - **Rationale:** data is provides but a programmed sensor, if we're not talking about a rare bitfilp or anything physical, sensor value should be numerical 
  - **Alternative considered:** [What else you thought about]

- **Assumption 2:** units are always the same ( °C or Kelvin for exp ) so i dont have to do the conversion
  - **Rationale:** usually we're using the same type of sensors programmed the same way, they should have fixed units, still could be possible for one sensor to be different, so could've been better to do the conversion..

### Anomaly Detection
- **Method choice:** Implemented the z-score method because it is a simple and interpretable statistical approach for detecting outliers. It allows us to flag readings that deviate significantly from the sensor’s normal behavior. Rolling and IQR methods were considered but not implemented due to time constraints.
- **Threshold handling:** The threshold parameter determines how many standard deviations away from the mean a reading must be to be considered anomalous. Edge cases are handled, such as:
Zero standard deviation: If all readings are identical, division by zero is avoided and no anomalies are flagged.

All readings extreme: The method can flag all readings as anomalies if they all deviate from the mean, which reflects potential sensor drift.
- **Missing data:** Rows with missing value (NaN) are dropped during ingestion, so anomaly detection only uses valid numeric readings. This ensures calculations like mean and standard deviation are accurate. Any remaining UNCERTAIN readings with valid numeric values are still included in the detection.

### Metrics Summarization
- **Metric selection:** [Which metrics you chose and why]
- **Aggregation strategy:** [How you aggregate data]

---

## ⚠️ Known Limitations

Be honest about what doesn't work perfectly or edge cases you didn't handle.

### Edge Cases Not Fully Handled
1. **[Edge case 1]:** All values for a sensor are NaN
   - **Impact:** If an entire sensor column is empty, ingestion will remove all rows, and anomaly detection will have no data to process.
   - **Workaround:** Workaround: Currently, the function raises a warning or simply returns an empty DataFrame. A more robust solution would be to log the missing sensor and skip it gracefully.

2. **[Edge case 2]:** All readings are anomalous
   - **Impact:** If every reading exceeds the anomaly threshold, the z-score method will flag all as anomalies, which might not distinguish between true outliers and a shifted baseline.
   - **Workaround:** Could implement a check for “anomaly ratio” and treat very high ratios as a trend shift rather than isolated anomalies.

### Performance Considerations
- **Large datasets:** [How your code scales, any concerns]
- **Memory usage:** [Any memory-intensive operations]

---

## 🚀 Next Steps

If you had more time, what would you improve or add?

### Priority 1: [Highest priority improvement]
- **What:** [Description]
- **Why:** [Impact/value]
- **Estimated effort:** [Time estimate]

### Priority 2: [Second priority]
- **What:**
- **Why:**
- **Estimated effort:**

### Additional Features
- [Feature idea 1]
- [Feature idea 2]

### Testing & Validation
- [What additional tests you'd write]
- [What validation you'd add]

---

## ❓ Questions for the Team

List any clarifying questions or areas where you'd like feedback.

1. **[Question about requirements]:** [e.g., "In production, how should we handle persistent connection failures?"]

2. **[Question about design]:** [e.g., "Would you prefer aggressive duplicate removal or conservative approach?"]

3. **[Technical question]:** [e.g., "Are there specific anomaly detection methods you use in production?"]

---

## 💡 Interesting Challenges

What did you find most interesting or challenging about this exercise?

- **Most challenging:** [What was hardest and why]
- **Most interesting:** [What you enjoyed working on]
- **Learned:** [Anything new you learned or researched]

---

## 🔧 Development Environment

Document your setup for reproducibility.

- **Python version:** [e.g., 3.11.5]
- **OS:** [e.g., Windows 11, Ubuntu 22.04, macOS]
- **Editor/IDE:** [e.g., VS Code, PyCharm]
- **Additional tools:** [e.g., "Used black for formatting", "Ran mypy for type checking"]

---

## 📚 References

Any resources you consulted (documentation, articles, etc.).

- [Resource 1 with link]
- [Resource 2 with link]

---

## 💭 Final Thoughts

Any additional context you want reviewers to know.

[Your thoughts here]

---

**Thank you for the opportunity!** I look forward to discussing this implementation.
