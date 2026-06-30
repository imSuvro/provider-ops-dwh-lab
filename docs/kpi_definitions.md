# KPI Definitions

These definitions describe the current learning-project metrics. They use only
synthetic data and are not production billing, clinical, financial, or
compliance rules. A business owner should approve the definitions, exclusions,
targets, and reporting cadence before they are used outside this lab.

## Shared conventions

- A **patient-month** is one patient, one program, and one calendar month.
- Monthly status checks use the end of the patient-month as the cutoff.
- Patient counts are distinct within the stated reporting dimensions.
- Customer, provider, program, and month filters should be applied before
  comparing KPI values.
- A percentage with a zero denominator should be reported as `NULL`, not zero.

## Active Patients

**Definition:** Distinct patients whose latest available enrollment for the
program is `ACTIVE` and whose enrollment status timestamp is before the end of
the patient-month.

**Formula:**

```text
count(distinct patient_id where is_active_enrollment = true)
```

**Primary grain:** Customer, program, and patient-month.

**Implemented fields:**

- `marts.mart_patient_month.is_active_enrollment`
- `marts.mart_clinic_or_customer_performance.active_patient_count`

**Interpretation:** This is an operational enrollment measure. It does not
prove clinical participation, device use, consent, or billability.

**Current limitation:** The synthetic source stores the latest enrollment
record rather than a complete status-change history. Historical reconstruction
will need a source that retains every status transition.

## Consented Patients

**Definition:** Distinct patients with a consent status of `COMPLETED` and a
completion timestamp before the end of the patient-month.

**Formula:**

```text
count(distinct patient_id where has_completed_consent = true)
```

**Primary grain:** Customer, program, and patient-month.

**Implemented fields:**

- `marts.mart_patient_month.has_completed_consent`
- `marts.mart_clinic_or_customer_performance.consented_patient_count`

**Interpretation:** This measures documented completion in the available
source. It does not determine whether the consent language, method, or version
meets a production policy.

## Enrollment Conversion %

**Definition:** The share of current enrollment records that have reached
`ACTIVE`.

**Proposed formula:**

```text
100 * active enrollment_count / total enrollment_count
```

where:

```text
active enrollment_count =
  sum(enrollment_count where enrollment_status = 'ACTIVE')

total enrollment_count =
  sum(enrollment_count across all enrollment statuses)
```

**Primary grain:** Customer, provider, and program. Add a cohort or reporting
period only after a reliable status-history source exists.

**Source model:** `marts.mart_enrollment_funnel`.

**Interpretation:** The current formula is a snapshot conversion ratio, not a
time-to-conversion or cohort conversion metric.

**Decision needed:** Confirm whether declined enrollments remain in the
denominator, which status counts as conversion, and whether conversion should
be measured by enrollment or distinct patient.

## Timer Utilization

**Definition:** Recorded timer minutes as a share of the program minimum for
active patient-months with a positive minute requirement.

**Proposed formula:**

```text
100 * sum(timer_minutes) / sum(monthly_minimum_minutes)
```

Include only rows where:

```text
is_active_enrollment = true
and monthly_minimum_minutes > 0
```

**Primary grain:** Customer, program, and patient-month. It can also be
inspected at patient-month grain.

**Source fields:**

- `marts.mart_patient_month.timer_minutes`
- `marts.mart_patient_month.monthly_minimum_minutes`
- `marts.mart_patient_month.has_required_minutes`
- `marts.mart_clinic_or_customer_performance.timer_minutes`

**Interpretation:** Values may exceed 100% because the current definition does
not cap minutes at the minimum. This makes over-threshold activity visible.

**Decision needed:** Confirm whether utilization should be capped, whether all
activity types count, and whether only approved or billable time is eligible.

## Device Fulfillment Delay

**Definition:** Distinct patients whose latest available device order has a
status of `DELAYED`.

**Current formula:**

```text
count(distinct patient_id where device_status = 'DELAYED')
```

**Primary grain:** Customer, program, and patient-month.

**Implemented fields:**

- `marts.mart_patient_month.device_status`
- `marts.mart_clinic_or_customer_performance.delayed_device_count`

**Interpretation:** This is a delayed-order count, not elapsed fulfillment
time.

**Decision needed:** A true duration KPI requires promised, shipped, and
delivered timestamps plus an agreed service-level target. Confirm whether the
desired measure is delayed count, delayed rate, average days to delivery, or
all three.

## Billable Patient-Month

**Definition:** A patient-program-month that meets every local readiness rule:

1. The program is recognized.
2. Enrollment is active by month-end.
3. Consent is completed by month-end.
4. Recorded timer minutes meet the program minimum.
5. If the program requires a device, its latest available status is
   `DELIVERED` by month-end.

**Formula:**

```text
is_billable_ready =
  recognized program
  and is_active_enrollment
  and has_completed_consent
  and has_required_minutes
  and is_device_ready
```

**Primary grain:** Patient, program, and patient-month.

**Implemented fields and models:**

- `marts.mart_patient_month.is_billable_ready`
- `marts.mart_billable_activity`
- `marts.mart_clinic_or_customer_performance.billable_ready_patient_count`

**Important distinction:** `source_billable_candidate` comes from the
synthetic billing export and is retained for comparison. It is not an input to
the computed readiness rule.

**Decision needed:** A billing owner must confirm program-specific codes,
thresholds, exclusions, payer rules, carry-forward behavior, and whether
device delivery is required for each program.

## Customer Performance

**Definition:** A monthly scorecard for a customer and program, rather than a
single opaque score.

**Scorecard measures:**

- `patient_count`
- `active_patient_count`
- `consented_patient_count`
- `timer_minutes`
- `delayed_device_count`
- `billable_candidate_count`
- `billable_ready_patient_count`
- `billable_readiness_rate`

**Primary grain:** Customer, program, and patient-month.

**Source model:** `marts.mart_clinic_or_customer_performance`.

**Current readiness-rate formula:**

```text
billable_ready_patient_count / patient_count
```

**Interpretation:** The measures should be read together. The project does not
assign a weighted performance score because weights and targets require
business ownership.

**Decision needed:** Confirm targets, red/amber/green thresholds, whether
provider comparisons are appropriate, and who owns remediation for each
measure.

## Ownership and approval

The business owner, technical owner, source-of-truth system, refresh target,
and approval status for every KPI remain open. Track those decisions in
[`open_questions_for_cto.md`](open_questions_for_cto.md) before treating these
definitions as production requirements.
