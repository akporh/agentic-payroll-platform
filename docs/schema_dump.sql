--
-- PostgreSQL database dump
--

\restrict 9DK1XYbmRzbWwQDo4FNwPyqdJ8sghjYAVbf7UQ2467Y8FFdOxVh6QjbYcEd89d3

-- Dumped from database version 15.16 (Homebrew)
-- Dumped by pg_dump version 15.16 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: derivation_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.derivation_status AS ENUM (
    'PENDING',
    'DERIVED',
    'APPROVED',
    'FAILED'
);


--
-- Name: workspace_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.workspace_status AS ENUM (
    'DRAFT',
    'STRUCTURE_DEFINED',
    'COMPENSATION_DEFINED',
    'RULES_DEFINED',
    'READY',
    'LIVE'
);


--
-- Name: enforce_payroll_readiness(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.enforce_payroll_readiness() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        v_result jsonb;
        v_ready boolean;
    BEGIN

        v_result := validate_payroll_readiness(
            NEW.workspace_id,
            NEW.period_start,
            NEW.period_end
        );

        v_ready := (v_result->>'ready')::boolean;

        IF v_ready IS FALSE THEN
            RAISE EXCEPTION
            'Payroll readiness failed: %',
            v_result->>'errors';
        END IF;

        RETURN NEW;
    END;
    $$;


--
-- Name: enforce_payroll_run_initial_status(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.enforce_payroll_run_initial_status() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF NEW.status <> 'DRAFT' THEN
                RAISE EXCEPTION
                    'New payroll runs must be created with status DRAFT. Got: %.',
                    NEW.status;
            END IF;
            RETURN NEW;
        END;
        $$;


--
-- Name: enforce_workspace_live_before_payroll(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.enforce_workspace_live_before_payroll() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        DECLARE
            v_status workspace_status;
        BEGIN

            SELECT status INTO v_status
            FROM workspace
            WHERE workspace_id = NEW.workspace_id;

            IF v_status IS DISTINCT FROM 'LIVE' THEN
                RAISE EXCEPTION
                    'Cannot create payroll_run: workspace % is not LIVE (current status: %)',
                    NEW.workspace_id,
                    v_status;
            END IF;

            RETURN NEW;
        END;
        $$;


--
-- Name: prevent_paid_payroll_run_update(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.prevent_paid_payroll_run_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RAISE EXCEPTION 
            'Payroll run % is PAID and cannot be modified',
            OLD.payroll_run_id;
    END;
    $$;


--
-- Name: prevent_payroll_result_mutation(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.prevent_payroll_result_mutation() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        DECLARE
            v_run_id UUID;
            v_status TEXT;
        BEGIN
            -- Works for both UPDATE (NEW is available) and DELETE (NEW is NULL)
            v_run_id := COALESCE(NEW.payroll_run_id, OLD.payroll_run_id);

            SELECT status INTO v_status
            FROM   payroll_run
            WHERE  payroll_run_id = v_run_id;

            IF v_status IN ('CALCULATED', 'APPROVED', 'LOCKED', 'PAID') THEN
                RAISE EXCEPTION
                    'Payroll results are immutable after calculation. '
                    'Run % has status %.',
                    v_run_id,
                    v_status;
            END IF;

            -- Allow the operation
            RETURN COALESCE(NEW, OLD);
        END;
        $$;


--
-- Name: prevent_result_modification_if_paid(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.prevent_result_modification_if_paid() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        parent_status TEXT;
    BEGIN
        SELECT status INTO parent_status
        FROM payroll_run
        WHERE payroll_run_id = COALESCE(NEW.payroll_run_id, OLD.payroll_run_id);

        IF parent_status = 'PAID' THEN
            RAISE EXCEPTION
            'Cannot modify payroll_result because parent payroll_run is PAID';
        END IF;

        RETURN COALESCE(NEW, OLD);
    END;
    $$;


--
-- Name: prevent_run_snapshot_update(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.prevent_run_snapshot_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        IF NEW.rules_context_snapshot IS DISTINCT FROM OLD.rules_context_snapshot THEN
            RAISE EXCEPTION 'rules_context_snapshot is immutable';
        END IF;
        RETURN NEW;
    END;
    $$;


--
-- Name: prevent_salary_definition_change_if_used(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.prevent_salary_definition_change_if_used() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        used_count INTEGER;
    BEGIN
        SELECT COUNT(*) INTO used_count
        FROM employee_contract ec
        JOIN payroll_result pr ON pr.employee_id = ec.employee_id
        JOIN payroll_run run ON run.payroll_run_id = pr.payroll_run_id
        WHERE ec.salary_definition_id = OLD.salary_definition_id
          AND run.status = 'PAID';

        IF used_count > 0 THEN
            RAISE EXCEPTION 
            'Cannot modify salary_definition % because it was used in a PAID payroll',
            OLD.salary_definition_id;
        END IF;

        RETURN COALESCE(NEW, OLD);
    END;
    $$;


--
-- Name: prevent_snapshot_update(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.prevent_snapshot_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        IF NEW.calculations_snapshot_json IS DISTINCT FROM OLD.calculations_snapshot_json THEN
            RAISE EXCEPTION 'calculations_snapshot_json is immutable';
        END IF;

        RETURN NEW;
    END;
    $$;


--
-- Name: validate_payroll_readiness(uuid, date, date); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_payroll_readiness(p_workspace_id uuid, p_period_start date, p_period_end date) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
    DECLARE
        v_errors jsonb := '[]'::jsonb;
        v_count  integer;
        v_country character varying;
    BEGIN

        ----------------------------------------------------------------
        -- LAYER 0: WORKSPACE STATE
        ----------------------------------------------------------------
        SELECT COUNT(*) INTO v_count
        FROM workspace
        WHERE workspace_id = p_workspace_id
          AND status = 'LIVE';

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code',    'WORKSPACE_NOT_LIVE',
                'message', 'Workspace must be LIVE before running payroll.'
            );
        END IF;

        ----------------------------------------------------------------
        -- LAYER 1: STATUTORY CONFIGURATION
        ----------------------------------------------------------------
        SELECT COUNT(*) INTO v_count FROM statutory_rule;

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code',    'NO_STATUTORY_RULE',
                'message', 'No statutory rule configured.'
            );
        END IF;

        SELECT COUNT(*) INTO v_count FROM tax_band;

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code',    'NO_TAX_BANDS',
                'message', 'No tax bands configured.'
            );
        END IF;

        ----------------------------------------------------------------
        -- LAYER 2: COMPONENT METADATA
        ----------------------------------------------------------------
        SELECT country_code INTO v_country
        FROM workspace
        WHERE workspace_id = p_workspace_id;

        SELECT COUNT(*) INTO v_count
        FROM component_metadata
        WHERE country_code = v_country
          AND is_active = true;

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code',    'NO_ACTIVE_COMPONENT_METADATA',
                'message', 'No active component metadata configured.'
            );
        END IF;

        ----------------------------------------------------------------
        -- RETURN
        ----------------------------------------------------------------
        IF jsonb_array_length(v_errors) = 0 THEN
            RETURN jsonb_build_object('ready', true,  'errors', '[]'::jsonb);
        ELSE
            RETURN jsonb_build_object('ready', false, 'errors', v_errors);
        END IF;

    END;
    $$;


--
-- Name: validate_payroll_status_transition(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_payroll_status_transition() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        DECLARE
            v_old_rank INT;
            v_new_rank INT;
        BEGIN
            -- Resolve lifecycle rank for the current status.
            SELECT position INTO v_old_rank
            FROM (VALUES
                ('DRAFT',       1),
                ('VALIDATED',   2),
                ('CALCULATING', 2),
                ('PARTIAL',     3),
                ('CALCULATED',  4),
                ('APPROVED',    5),
                ('LOCKED',      6),
                ('PAID',        7)
            ) AS lifecycle(status, position)
            WHERE status = OLD.status;

            -- Resolve lifecycle rank for the target status.
            SELECT position INTO v_new_rank
            FROM (VALUES
                ('DRAFT',       1),
                ('VALIDATED',   2),
                ('CALCULATING', 2),
                ('PARTIAL',     3),
                ('CALCULATED',  4),
                ('APPROVED',    5),
                ('LOCKED',      6),
                ('PAID',        7)
            ) AS lifecycle(status, position)
            WHERE status = NEW.status;

            -- Reject unknown status values immediately.
            IF v_old_rank IS NULL THEN
                RAISE EXCEPTION
                    'Unknown payroll run status: %. '
                    'Valid statuses: DRAFT, VALIDATED, CALCULATING, PARTIAL, '
                    'CALCULATED, APPROVED, LOCKED, PAID.',
                    OLD.status;
            END IF;

            IF v_new_rank IS NULL THEN
                RAISE EXCEPTION
                    'Unknown payroll run status: %. '
                    'Valid statuses: DRAFT, VALIDATED, CALCULATING, PARTIAL, '
                    'CALCULATED, APPROVED, LOCKED, PAID.',
                    NEW.status;
            END IF;

            -- Enforce forward-only progression.
            -- PAID (rank 7) is terminal: nothing has a higher rank,
            -- so any transition FROM PAID fails here.
            IF v_new_rank < v_old_rank THEN
                RAISE EXCEPTION
                    'Invalid payroll run status transition: % → %. '
                    'Status cannot move backwards. '
                    'Allowed forward transitions: '
                    'DRAFT → VALIDATED → CALCULATED → APPROVED → PAID.',
                    OLD.status, NEW.status;
            END IF;

            RETURN NEW;
        END;
        $$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: account; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.account (
    account_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: attendance_code_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.attendance_code_config (
    attendance_code_config_id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid NOT NULL,
    client_code character varying(20) NOT NULL,
    description character varying(200),
    category character varying(10) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT attendance_code_config_category_check CHECK (((category)::text = ANY ((ARRAY['WORK'::character varying, 'LEAVE'::character varying, 'OT'::character varying, 'SHIFT'::character varying])::text[])))
);


--
-- Name: attendance_policy_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.attendance_policy_config (
    attendance_policy_config_id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid NOT NULL,
    client_code character varying(20) NOT NULL,
    counts_as_paid boolean DEFAULT true NOT NULL,
    counts_towards_ot_threshold boolean DEFAULT true NOT NULL,
    hours_equivalent numeric(5,2),
    unit_fraction numeric(5,4),
    eligible_for_shift_allowance boolean DEFAULT false NOT NULL,
    eligible_for_ot boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT attendance_policy_config_check CHECK ((NOT ((counts_as_paid = false) AND (counts_towards_ot_threshold = true)))),
    CONSTRAINT attendance_policy_config_check1 CHECK ((NOT ((hours_equivalent IS NOT NULL) AND (unit_fraction IS NOT NULL)))),
    CONSTRAINT attendance_policy_config_hours_equivalent_check CHECK (((hours_equivalent IS NULL) OR (hours_equivalent > (0)::numeric))),
    CONSTRAINT attendance_policy_config_unit_fraction_check CHECK (((unit_fraction IS NULL) OR ((unit_fraction > (0)::numeric) AND (unit_fraction <= (1)::numeric))))
);


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log (
    audit_log_id uuid NOT NULL,
    workspace_id uuid,
    entity_type character varying NOT NULL,
    entity_id uuid NOT NULL,
    action character varying NOT NULL,
    old_value_jsonb jsonb,
    new_value_jsonb jsonb,
    performed_by character varying NOT NULL,
    performed_at timestamp without time zone DEFAULT now()
);


--
-- Name: client_component_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client_component_metadata (
    client_component_metadata_id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid NOT NULL,
    component_code text NOT NULL,
    overrides_json jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    is_active boolean DEFAULT true NOT NULL,
    proration_strategy character varying(50),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: component_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.component_metadata (
    component_metadata_id uuid NOT NULL,
    country_code character varying(10) NOT NULL,
    version integer NOT NULL,
    metadata_json jsonb NOT NULL,
    effective_from date NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    component_code text NOT NULL,
    component_class text,
    calculation_method text,
    execution_priority integer,
    CONSTRAINT ck_component_metadata_class CHECK (((component_class IS NULL) OR (component_class = ANY (ARRAY['earning'::text, 'statutory_deduction'::text, 'aggregate'::text, 'final'::text, 'statutory_relief'::text, 'employer_cost'::text, 'non_taxable'::text, 'paye_addition'::text]))))
);


--
-- Name: designation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.designation (
    designation_id uuid NOT NULL,
    workspace_id uuid NOT NULL,
    designation_code character varying(100) NOT NULL,
    description character varying(255),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: employee; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee (
    employee_id uuid NOT NULL,
    workspace_id uuid,
    full_name character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    status character varying(20),
    personal_details_encrypted jsonb,
    employee_number character varying(50)
);


--
-- Name: employee_contract; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_contract (
    contract_id uuid NOT NULL,
    employee_id uuid NOT NULL,
    salary_definition_id uuid NOT NULL,
    grade_id uuid,
    start_date date NOT NULL,
    end_date date,
    change_reason character varying(255),
    designation_id uuid,
    shift_type character varying(10),
    state_of_tax character varying(50),
    skill_level character varying(50),
    is_union_member boolean DEFAULT false NOT NULL,
    CONSTRAINT chk_employee_contract_shift_type CHECK (((shift_type)::text = ANY ((ARRAY['DAY'::character varying, '2_SHIFT'::character varying, '4_SHIFT'::character varying])::text[])))
);


--
-- Name: event_store; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.event_store (
    event_id uuid NOT NULL,
    aggregate_type character varying NOT NULL,
    aggregate_id uuid NOT NULL,
    event_type character varying NOT NULL,
    event_payload jsonb NOT NULL,
    occurred_at timestamp without time zone DEFAULT now(),
    workspace_id uuid
);


--
-- Name: execution_trace; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.execution_trace (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    run_id uuid NOT NULL,
    step_name character varying(200) NOT NULL,
    status character varying(20) NOT NULL,
    duration_ms integer,
    error_message text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: grade; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.grade (
    grade_id uuid NOT NULL,
    workspace_id uuid NOT NULL,
    grade_code character varying(50) NOT NULL,
    description character varying(255),
    updated_at timestamp with time zone DEFAULT now(),
    total_monthly numeric(15,2),
    basic_pct numeric(5,4),
    housing_pct numeric(5,4),
    transport_pct numeric(5,4),
    utility_pct numeric(5,4),
    CONSTRAINT chk_grade_pct_completeness CHECK (((total_monthly IS NULL) OR ((basic_pct IS NOT NULL) AND (housing_pct IS NOT NULL) AND (transport_pct IS NOT NULL) AND (utility_pct IS NOT NULL) AND (abs(((((basic_pct + housing_pct) + transport_pct) + utility_pct) - 1.0)) < 0.0001))))
);


--
-- Name: national_public_holiday; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.national_public_holiday (
    holiday_id uuid DEFAULT gen_random_uuid() NOT NULL,
    country_code text NOT NULL,
    holiday_date date NOT NULL,
    name text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: pay_cycle; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pay_cycle (
    pay_cycle_id uuid NOT NULL,
    workspace_id uuid NOT NULL,
    frequency character varying(20) NOT NULL,
    run_day integer NOT NULL,
    cutoff_day integer NOT NULL,
    payment_day integer NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    definition_json jsonb,
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: payroll_input; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payroll_input (
    payroll_input_id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid NOT NULL,
    payroll_run_id uuid,
    employee_id uuid NOT NULL,
    input_code character varying(50) NOT NULL,
    input_category character varying(30) NOT NULL,
    quantity numeric(12,2),
    rate numeric(12,2),
    amount numeric(12,2),
    reference_date date,
    source character varying(50) DEFAULT 'MANUAL'::character varying,
    input_json jsonb,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT ck_payroll_input_category CHECK (((input_category)::text = ANY ((ARRAY['EARNING'::character varying, 'DEDUCTION'::character varying, 'STANDARD'::character varying, 'PAYE_ONLY'::character varying])::text[]))),
    CONSTRAINT ck_payroll_input_json_object CHECK (((input_json IS NULL) OR (jsonb_typeof(input_json) = 'object'::text))),
    CONSTRAINT ck_payroll_input_quantity_non_negative CHECK ((quantity >= (0)::numeric))
);


--
-- Name: payroll_reconciliation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payroll_reconciliation (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    payroll_run_id uuid NOT NULL,
    expected_total numeric(18,2) NOT NULL,
    actual_total numeric(18,2),
    status text NOT NULL,
    reconciled_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    notes text,
    resolved_by character varying(255),
    resolved_at timestamp without time zone,
    CONSTRAINT chk_matched_totals_equal CHECK (((status <> 'MATCHED'::text) OR (actual_total = expected_total))),
    CONSTRAINT chk_mismatch_totals_differ CHECK (((status <> 'MISMATCH'::text) OR (actual_total <> expected_total))),
    CONSTRAINT chk_reconciliation_status CHECK ((status = ANY (ARRAY['PENDING'::text, 'MATCHED'::text, 'MISMATCH'::text, 'RESOLVED'::text]))),
    CONSTRAINT chk_resolved_audit_fields CHECK (((status <> 'RESOLVED'::text) OR ((resolved_by IS NOT NULL) AND (resolved_at IS NOT NULL))))
);


--
-- Name: payroll_result; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payroll_result (
    payroll_result_id uuid NOT NULL,
    payroll_run_id uuid,
    employee_id uuid,
    gross_components_jsonb jsonb NOT NULL,
    deductions_jsonb jsonb NOT NULL,
    net_pay numeric NOT NULL,
    calculations_snapshot_json jsonb NOT NULL,
    generated_at timestamp without time zone DEFAULT now(),
    status character varying(20) NOT NULL,
    error_message text,
    component_trace_jsonb jsonb,
    per_employee_context_json jsonb,
    CONSTRAINT chk_calculation_snapshot_is_object CHECK ((jsonb_typeof(calculations_snapshot_json) = 'object'::text)),
    CONSTRAINT chk_deductions_is_object CHECK ((jsonb_typeof(deductions_jsonb) = 'object'::text)),
    CONSTRAINT chk_gross_components_is_object CHECK ((jsonb_typeof(gross_components_jsonb) = 'object'::text))
);


--
-- Name: payroll_rule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payroll_rule (
    rule_id uuid NOT NULL,
    workspace_id uuid,
    rule_name character varying(255) NOT NULL,
    rule_definition_json jsonb NOT NULL,
    rule_type character varying(100),
    schema_version integer DEFAULT 1,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT chk_payroll_rule_calculation_method CHECK ((((rule_definition_json ->> 'calculation_method'::text) IS NULL) OR ((rule_definition_json ->> 'calculation_method'::text) = ANY (ARRAY['unit_multiplier'::text, 'daily_rate_deduction'::text, 'fixed_amount'::text, 'ot_multiplier'::text, 'percentage_of_sum'::text])))),
    CONSTRAINT chk_rule_definition_is_object CHECK ((jsonb_typeof(rule_definition_json) = 'object'::text))
);


--
-- Name: payroll_run; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payroll_run (
    payroll_run_id uuid NOT NULL,
    workspace_id uuid,
    status character varying(50) NOT NULL,
    rules_context_snapshot jsonb,
    created_at timestamp without time zone DEFAULT now(),
    period_start date,
    period_end date,
    pay_date date,
    total_gross_pay numeric(18,2) DEFAULT 0 NOT NULL,
    total_deduction numeric(18,2) DEFAULT 0 NOT NULL,
    total_net_pay numeric(18,2) DEFAULT 0 NOT NULL,
    idempotency_key text,
    total_tax numeric(18,2) DEFAULT 0 NOT NULL,
    retry_strategy character varying(20) DEFAULT 'PER_EMPLOYEE'::character varying NOT NULL,
    rule_set_id uuid,
    statutory_effective_date date,
    run_type text DEFAULT 'REGULAR'::text NOT NULL,
    CONSTRAINT ck_payroll_run_retry_strategy CHECK (((retry_strategy)::text = ANY ((ARRAY['PER_EMPLOYEE'::character varying, 'FULL_RUN'::character varying])::text[])))
);


--
-- Name: platform_attendance_code_template; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.platform_attendance_code_template (
    client_code character varying(20) NOT NULL,
    description character varying(200),
    category character varying(10) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    introduced_in_version character varying(10) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT platform_attendance_code_template_category_check CHECK (((category)::text = ANY ((ARRAY['WORK'::character varying, 'LEAVE'::character varying, 'OT'::character varying, 'SHIFT'::character varying])::text[])))
);


--
-- Name: platform_attendance_policy_template; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.platform_attendance_policy_template (
    client_code character varying(20) NOT NULL,
    counts_as_paid boolean DEFAULT true NOT NULL,
    counts_towards_ot_threshold boolean DEFAULT true NOT NULL,
    hours_equivalent numeric(5,2),
    unit_fraction numeric(5,4),
    eligible_for_shift_allowance boolean DEFAULT false NOT NULL,
    eligible_for_ot boolean DEFAULT false NOT NULL,
    introduced_in_version character varying(10) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT platform_attendance_policy_template_check CHECK ((NOT ((counts_as_paid = false) AND (counts_towards_ot_threshold = true)))),
    CONSTRAINT platform_attendance_policy_template_check1 CHECK ((NOT ((hours_equivalent IS NOT NULL) AND (unit_fraction IS NOT NULL)))),
    CONSTRAINT platform_attendance_policy_template_hours_equivalent_check CHECK (((hours_equivalent IS NULL) OR (hours_equivalent > (0)::numeric))),
    CONSTRAINT platform_attendance_policy_template_unit_fraction_check CHECK (((unit_fraction IS NULL) OR ((unit_fraction > (0)::numeric) AND (unit_fraction <= (1)::numeric))))
);


--
-- Name: platform_attendance_template_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.platform_attendance_template_version (
    version_tag character varying(10) NOT NULL,
    released_at timestamp with time zone DEFAULT now() NOT NULL,
    notes character varying(500)
);


--
-- Name: rate_code_registry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rate_code_registry (
    rate_code_id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid,
    code text NOT NULL,
    multiplier numeric(8,4) NOT NULL,
    unit text NOT NULL,
    base text NOT NULL,
    description text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_rcr_base CHECK ((base = ANY (ARRAY['basic_hourly'::text, 'basic_daily'::text]))),
    CONSTRAINT ck_rcr_unit CHECK ((unit = ANY (ARRAY['hour'::text, 'day'::text])))
);


--
-- Name: rule_set; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rule_set (
    rule_set_id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid NOT NULL,
    effective_from date NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid NOT NULL
);


--
-- Name: rule_set_item; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rule_set_item (
    rule_set_id uuid NOT NULL,
    rule_name text NOT NULL,
    rule_definition_json jsonb NOT NULL,
    rule_type text
);


--
-- Name: salary_definition; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.salary_definition (
    salary_definition_id uuid NOT NULL,
    components_jsonb jsonb NOT NULL,
    workspace_id uuid,
    name character varying(255),
    schema_version integer DEFAULT 1,
    effective_from date,
    effective_to date,
    code character varying(120) NOT NULL,
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT chk_salary_components_is_object CHECK ((jsonb_typeof(components_jsonb) = 'object'::text)),
    CONSTRAINT chk_salary_definition_basic_required CHECK ((components_jsonb ? 'BASIC'::text))
);


--
-- Name: statutory_rule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.statutory_rule (
    statutory_rule_id uuid NOT NULL,
    state character varying(50) NOT NULL,
    version integer NOT NULL,
    rules_jsonb jsonb NOT NULL,
    tax_method character varying(30) DEFAULT 'CUMULATIVE'::character varying NOT NULL,
    country_code character varying(10),
    effective_from date DEFAULT '2000-01-01'::date NOT NULL,
    CONSTRAINT chk_statutory_rule_no_tax_bands_in_jsonb CHECK ((NOT (rules_jsonb ? 'tax_bands'::text)))
);


--
-- Name: tax_band; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tax_band (
    tax_band_id uuid NOT NULL,
    statutory_rule_id uuid,
    lower_limit numeric NOT NULL,
    upper_limit numeric,
    rate numeric NOT NULL,
    CONSTRAINT chk_tax_band_lower_non_negative CHECK ((lower_limit >= (0)::numeric)),
    CONSTRAINT chk_tax_band_valid_range CHECK (((upper_limit IS NULL) OR (upper_limit > lower_limit)))
);


--
-- Name: timesheet_entry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.timesheet_entry (
    timesheet_entry_id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid NOT NULL,
    employee_id uuid NOT NULL,
    period_start date NOT NULL,
    period_end date NOT NULL,
    attendance_grid_jsonb jsonb NOT NULL,
    derivation_status public.derivation_status DEFAULT 'PENDING'::public.derivation_status NOT NULL,
    derivation_error text,
    policy_snapshot_jsonb jsonb,
    derivation_summary_jsonb jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: workspace; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workspace (
    workspace_id uuid NOT NULL,
    account_id uuid,
    name character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    country_code character varying(10),
    base_currency character varying(10),
    status public.workspace_status DEFAULT 'DRAFT'::public.workspace_status NOT NULL,
    attendance_template_version character varying(10)
);


--
-- Name: workspace_payroll_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workspace_payroll_config (
    config_id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid NOT NULL,
    effective_from date DEFAULT CURRENT_DATE NOT NULL,
    ph_mode text DEFAULT 'FILE_BASED'::text NOT NULL,
    ph_rate_code text DEFAULT 'OT005'::text NOT NULL,
    saturday_ph_rule text DEFAULT 'PH_TAKES_PRECEDENCE'::text NOT NULL,
    sunday_ph_rule text DEFAULT 'PH_TAKES_PRECEDENCE'::text NOT NULL,
    d3_leave_overlap_rule text DEFAULT 'LEAVE_ABSORBS_PH'::text NOT NULL,
    d4_absence_rule text DEFAULT 'ABSENT_IS_DEDUCTIBLE'::text NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_by uuid,
    timesheet_enabled boolean DEFAULT false NOT NULL,
    CONSTRAINT ck_wpc_d3 CHECK ((d3_leave_overlap_rule = ANY (ARRAY['LEAVE_ABSORBS_PH'::text, 'PH_ADDITIVE'::text]))),
    CONSTRAINT ck_wpc_d4 CHECK ((d4_absence_rule = ANY (ARRAY['ABSENT_IS_DEDUCTIBLE'::text, 'PH_EXCUSES_ABSENCE'::text]))),
    CONSTRAINT ck_wpc_ph_mode CHECK ((ph_mode = ANY (ARRAY['AUTOMATIC'::text, 'FILE_BASED'::text]))),
    CONSTRAINT ck_wpc_sat_rule CHECK ((saturday_ph_rule = ANY (ARRAY['PH_TAKES_PRECEDENCE'::text, 'DAY_OF_WEEK_TAKES_PRECEDENCE'::text]))),
    CONSTRAINT ck_wpc_sun_rule CHECK ((sunday_ph_rule = ANY (ARRAY['PH_TAKES_PRECEDENCE'::text, 'DAY_OF_WEEK_TAKES_PRECEDENCE'::text])))
);


--
-- Name: workspace_public_holiday; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workspace_public_holiday (
    holiday_id uuid DEFAULT gen_random_uuid() NOT NULL,
    workspace_id uuid NOT NULL,
    holiday_date date NOT NULL,
    name text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: account account_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.account
    ADD CONSTRAINT account_pkey PRIMARY KEY (account_id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: attendance_code_config attendance_code_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance_code_config
    ADD CONSTRAINT attendance_code_config_pkey PRIMARY KEY (attendance_code_config_id);


--
-- Name: attendance_code_config attendance_code_config_workspace_id_client_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance_code_config
    ADD CONSTRAINT attendance_code_config_workspace_id_client_code_key UNIQUE (workspace_id, client_code);


--
-- Name: attendance_policy_config attendance_policy_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance_policy_config
    ADD CONSTRAINT attendance_policy_config_pkey PRIMARY KEY (attendance_policy_config_id);


--
-- Name: attendance_policy_config attendance_policy_config_workspace_id_client_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance_policy_config
    ADD CONSTRAINT attendance_policy_config_workspace_id_client_code_key UNIQUE (workspace_id, client_code);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (audit_log_id);


--
-- Name: client_component_metadata client_component_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_component_metadata
    ADD CONSTRAINT client_component_metadata_pkey PRIMARY KEY (client_component_metadata_id);


--
-- Name: component_metadata component_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.component_metadata
    ADD CONSTRAINT component_metadata_pkey PRIMARY KEY (component_metadata_id);


--
-- Name: designation designation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.designation
    ADD CONSTRAINT designation_pkey PRIMARY KEY (designation_id);


--
-- Name: employee_contract employee_contract_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_contract
    ADD CONSTRAINT employee_contract_pkey PRIMARY KEY (contract_id);


--
-- Name: employee employee_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_pkey PRIMARY KEY (employee_id);


--
-- Name: event_store event_store_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event_store
    ADD CONSTRAINT event_store_pkey PRIMARY KEY (event_id);


--
-- Name: execution_trace execution_trace_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.execution_trace
    ADD CONSTRAINT execution_trace_pkey PRIMARY KEY (id);


--
-- Name: grade grade_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade
    ADD CONSTRAINT grade_pkey PRIMARY KEY (grade_id);


--
-- Name: pay_cycle pay_cycle_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pay_cycle
    ADD CONSTRAINT pay_cycle_pkey PRIMARY KEY (pay_cycle_id);


--
-- Name: payroll_input payroll_input_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_input
    ADD CONSTRAINT payroll_input_pkey PRIMARY KEY (payroll_input_id);


--
-- Name: payroll_result payroll_result_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_result
    ADD CONSTRAINT payroll_result_pkey PRIMARY KEY (payroll_result_id);


--
-- Name: payroll_rule payroll_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_rule
    ADD CONSTRAINT payroll_rule_pkey PRIMARY KEY (rule_id);


--
-- Name: payroll_run payroll_run_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_run
    ADD CONSTRAINT payroll_run_pkey PRIMARY KEY (payroll_run_id);


--
-- Name: national_public_holiday pk_national_public_holiday; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.national_public_holiday
    ADD CONSTRAINT pk_national_public_holiday PRIMARY KEY (holiday_id);


--
-- Name: payroll_reconciliation pk_payroll_reconciliation; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_reconciliation
    ADD CONSTRAINT pk_payroll_reconciliation PRIMARY KEY (id);


--
-- Name: rate_code_registry pk_rate_code_registry; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rate_code_registry
    ADD CONSTRAINT pk_rate_code_registry PRIMARY KEY (rate_code_id);


--
-- Name: rule_set pk_rule_set; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rule_set
    ADD CONSTRAINT pk_rule_set PRIMARY KEY (rule_set_id);


--
-- Name: rule_set_item pk_rule_set_item; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rule_set_item
    ADD CONSTRAINT pk_rule_set_item PRIMARY KEY (rule_set_id, rule_name);


--
-- Name: workspace_payroll_config pk_workspace_payroll_config; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_payroll_config
    ADD CONSTRAINT pk_workspace_payroll_config PRIMARY KEY (config_id);


--
-- Name: workspace_public_holiday pk_workspace_public_holiday; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_public_holiday
    ADD CONSTRAINT pk_workspace_public_holiday PRIMARY KEY (holiday_id);


--
-- Name: platform_attendance_code_template platform_attendance_code_template_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.platform_attendance_code_template
    ADD CONSTRAINT platform_attendance_code_template_pkey PRIMARY KEY (client_code);


--
-- Name: platform_attendance_policy_template platform_attendance_policy_template_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.platform_attendance_policy_template
    ADD CONSTRAINT platform_attendance_policy_template_pkey PRIMARY KEY (client_code);


--
-- Name: platform_attendance_template_version platform_attendance_template_version_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.platform_attendance_template_version
    ADD CONSTRAINT platform_attendance_template_version_pkey PRIMARY KEY (version_tag);


--
-- Name: salary_definition salary_definition_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.salary_definition
    ADD CONSTRAINT salary_definition_pkey PRIMARY KEY (salary_definition_id);


--
-- Name: statutory_rule statutory_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.statutory_rule
    ADD CONSTRAINT statutory_rule_pkey PRIMARY KEY (statutory_rule_id);


--
-- Name: tax_band tax_band_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tax_band
    ADD CONSTRAINT tax_band_pkey PRIMARY KEY (tax_band_id);


--
-- Name: timesheet_entry timesheet_entry_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timesheet_entry
    ADD CONSTRAINT timesheet_entry_pkey PRIMARY KEY (timesheet_entry_id);


--
-- Name: timesheet_entry timesheet_entry_workspace_id_employee_id_period_start_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timesheet_entry
    ADD CONSTRAINT timesheet_entry_workspace_id_employee_id_period_start_key UNIQUE (workspace_id, employee_id, period_start);


--
-- Name: national_public_holiday uq_national_public_holiday_date; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.national_public_holiday
    ADD CONSTRAINT uq_national_public_holiday_date UNIQUE (country_code, holiday_date);


--
-- Name: payroll_reconciliation uq_reconciliation_run; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_reconciliation
    ADD CONSTRAINT uq_reconciliation_run UNIQUE (payroll_run_id);


--
-- Name: tax_band uq_tax_band_lower_limit; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tax_band
    ADD CONSTRAINT uq_tax_band_lower_limit UNIQUE (statutory_rule_id, lower_limit);


--
-- Name: workspace_payroll_config uq_workspace_payroll_config; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_payroll_config
    ADD CONSTRAINT uq_workspace_payroll_config UNIQUE (workspace_id, effective_from);


--
-- Name: workspace_public_holiday uq_workspace_public_holiday_date; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_public_holiday
    ADD CONSTRAINT uq_workspace_public_holiday_date UNIQUE (workspace_id, holiday_date);


--
-- Name: workspace workspace_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace
    ADD CONSTRAINT workspace_pkey PRIMARY KEY (workspace_id);


--
-- Name: idx_payroll_input_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payroll_input_code ON public.payroll_input USING btree (input_code);


--
-- Name: idx_payroll_input_employee; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payroll_input_employee ON public.payroll_input USING btree (employee_id);


--
-- Name: idx_payroll_input_period_unclaimed; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payroll_input_period_unclaimed ON public.payroll_input USING btree (workspace_id, reference_date) WHERE (payroll_run_id IS NULL);


--
-- Name: idx_payroll_input_run; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payroll_input_run ON public.payroll_input USING btree (payroll_run_id);


--
-- Name: idx_rule_set_workspace_effective; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rule_set_workspace_effective ON public.rule_set USING btree (workspace_id, effective_from DESC, created_at DESC);


--
-- Name: idx_salary_definition_components_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_salary_definition_components_gin ON public.salary_definition USING gin (components_jsonb);


--
-- Name: ix_attendance_policy_config_workspace_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_attendance_policy_config_workspace_code ON public.attendance_policy_config USING btree (workspace_id, client_code);


--
-- Name: ix_execution_trace_run_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_execution_trace_run_id ON public.execution_trace USING btree (run_id);


--
-- Name: ix_timesheet_entry_workspace_period; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_timesheet_entry_workspace_period ON public.timesheet_entry USING btree (workspace_id, period_start);


--
-- Name: uq_client_component_metadata_code_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_client_component_metadata_code_workspace ON public.client_component_metadata USING btree (workspace_id, component_code);


--
-- Name: uq_component_metadata_code_country_version; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_component_metadata_code_country_version ON public.component_metadata USING btree (component_code, country_code, version);


--
-- Name: uq_designation_code_per_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_designation_code_per_workspace ON public.designation USING btree (workspace_id, designation_code);


--
-- Name: uq_employee_active_contract; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_employee_active_contract ON public.employee_contract USING btree (employee_id) WHERE (end_date IS NULL);


--
-- Name: uq_employee_number_per_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_employee_number_per_workspace ON public.employee USING btree (workspace_id, employee_number);


--
-- Name: uq_grade_code_per_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_grade_code_per_workspace ON public.grade USING btree (workspace_id, grade_code);


--
-- Name: uq_pay_cycle_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_pay_cycle_workspace ON public.pay_cycle USING btree (workspace_id);


--
-- Name: uq_payroll_input_unclaimed; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_payroll_input_unclaimed ON public.payroll_input USING btree (workspace_id, employee_id, input_code, reference_date, source) WHERE (payroll_run_id IS NULL);


--
-- Name: uq_payroll_result_employee_run; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_payroll_result_employee_run ON public.payroll_result USING btree (payroll_run_id, employee_id);


--
-- Name: uq_payroll_run_regular; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_payroll_run_regular ON public.payroll_run USING btree (workspace_id, period_start, period_end) WHERE (run_type = 'REGULAR'::text);


--
-- Name: uq_rate_code_registry_workspace_code; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_rate_code_registry_workspace_code ON public.rate_code_registry USING btree (workspace_id, code);


--
-- Name: uq_salary_definition_code_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_salary_definition_code_workspace ON public.salary_definition USING btree (workspace_id, code);


--
-- Name: uq_salary_definition_name_per_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_salary_definition_name_per_workspace ON public.salary_definition USING btree (workspace_id, name);


--
-- Name: ux_payroll_run_idempotency; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ux_payroll_run_idempotency ON public.payroll_run USING btree (workspace_id, idempotency_key) WHERE (idempotency_key IS NOT NULL);


--
-- Name: payroll_run trg_enforce_payroll_readiness; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_enforce_payroll_readiness BEFORE INSERT ON public.payroll_run FOR EACH ROW EXECUTE FUNCTION public.enforce_payroll_readiness();


--
-- Name: payroll_run trg_enforce_payroll_run_initial_status; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_enforce_payroll_run_initial_status BEFORE INSERT ON public.payroll_run FOR EACH ROW EXECUTE FUNCTION public.enforce_payroll_run_initial_status();


--
-- Name: payroll_run trg_enforce_workspace_live; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_enforce_workspace_live BEFORE INSERT ON public.payroll_run FOR EACH ROW EXECUTE FUNCTION public.enforce_workspace_live_before_payroll();


--
-- Name: payroll_result trg_prevent_calculated_result_delete; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_prevent_calculated_result_delete BEFORE DELETE ON public.payroll_result FOR EACH ROW EXECUTE FUNCTION public.prevent_payroll_result_mutation();


--
-- Name: payroll_result trg_prevent_calculated_result_update; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_prevent_calculated_result_update BEFORE UPDATE ON public.payroll_result FOR EACH ROW EXECUTE FUNCTION public.prevent_payroll_result_mutation();


--
-- Name: payroll_result trg_prevent_paid_result_delete; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_prevent_paid_result_delete BEFORE DELETE ON public.payroll_result FOR EACH ROW EXECUTE FUNCTION public.prevent_result_modification_if_paid();


--
-- Name: payroll_result trg_prevent_paid_result_update; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_prevent_paid_result_update BEFORE UPDATE ON public.payroll_result FOR EACH ROW EXECUTE FUNCTION public.prevent_result_modification_if_paid();


--
-- Name: payroll_run trg_prevent_paid_run_delete; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_prevent_paid_run_delete BEFORE DELETE ON public.payroll_run FOR EACH ROW WHEN (((old.status)::text = 'PAID'::text)) EXECUTE FUNCTION public.prevent_paid_payroll_run_update();


--
-- Name: payroll_run trg_prevent_paid_run_update; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_prevent_paid_run_update BEFORE UPDATE ON public.payroll_run FOR EACH ROW WHEN (((old.status)::text = 'PAID'::text)) EXECUTE FUNCTION public.prevent_paid_payroll_run_update();


--
-- Name: salary_definition trg_prevent_salary_definition_delete; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_prevent_salary_definition_delete BEFORE DELETE ON public.salary_definition FOR EACH ROW EXECUTE FUNCTION public.prevent_salary_definition_change_if_used();


--
-- Name: salary_definition trg_prevent_salary_definition_update; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_prevent_salary_definition_update BEFORE UPDATE ON public.salary_definition FOR EACH ROW EXECUTE FUNCTION public.prevent_salary_definition_change_if_used();


--
-- Name: payroll_run trg_run_snapshot_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_run_snapshot_immutable BEFORE UPDATE OF rules_context_snapshot ON public.payroll_run FOR EACH ROW WHEN ((old.rules_context_snapshot IS DISTINCT FROM new.rules_context_snapshot)) EXECUTE FUNCTION public.prevent_run_snapshot_update();


--
-- Name: payroll_result trg_snapshot_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_snapshot_immutable BEFORE UPDATE OF calculations_snapshot_json ON public.payroll_result FOR EACH ROW WHEN ((old.calculations_snapshot_json IS DISTINCT FROM new.calculations_snapshot_json)) EXECUTE FUNCTION public.prevent_snapshot_update();


--
-- Name: payroll_run trg_validate_payroll_status_transition; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_validate_payroll_status_transition BEFORE UPDATE OF status ON public.payroll_run FOR EACH ROW WHEN (((old.status)::text IS DISTINCT FROM (new.status)::text)) EXECUTE FUNCTION public.validate_payroll_status_transition();


--
-- Name: attendance_code_config attendance_code_config_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance_code_config
    ADD CONSTRAINT attendance_code_config_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: attendance_policy_config attendance_policy_config_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance_policy_config
    ADD CONSTRAINT attendance_policy_config_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: audit_log audit_log_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: employee_contract employee_contract_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_contract
    ADD CONSTRAINT employee_contract_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(employee_id);


--
-- Name: employee_contract employee_contract_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_contract
    ADD CONSTRAINT employee_contract_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grade(grade_id);


--
-- Name: employee_contract employee_contract_salary_definition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_contract
    ADD CONSTRAINT employee_contract_salary_definition_id_fkey FOREIGN KEY (salary_definition_id) REFERENCES public.salary_definition(salary_definition_id);


--
-- Name: employee employee_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: client_component_metadata fk_client_component_metadata_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_component_metadata
    ADD CONSTRAINT fk_client_component_metadata_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: designation fk_designation_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.designation
    ADD CONSTRAINT fk_designation_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: employee_contract fk_employee_contract_designation; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_contract
    ADD CONSTRAINT fk_employee_contract_designation FOREIGN KEY (designation_id) REFERENCES public.designation(designation_id);


--
-- Name: payroll_input fk_input_employee; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_input
    ADD CONSTRAINT fk_input_employee FOREIGN KEY (employee_id) REFERENCES public.employee(employee_id);


--
-- Name: payroll_input fk_input_run; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_input
    ADD CONSTRAINT fk_input_run FOREIGN KEY (payroll_run_id) REFERENCES public.payroll_run(payroll_run_id);


--
-- Name: payroll_input fk_input_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_input
    ADD CONSTRAINT fk_input_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: pay_cycle fk_pay_cycle_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pay_cycle
    ADD CONSTRAINT fk_pay_cycle_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: attendance_policy_config fk_policy_to_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance_policy_config
    ADD CONSTRAINT fk_policy_to_code FOREIGN KEY (workspace_id, client_code) REFERENCES public.attendance_code_config(workspace_id, client_code);


--
-- Name: rule_set_item fk_rule_set_item_rule_set; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rule_set_item
    ADD CONSTRAINT fk_rule_set_item_rule_set FOREIGN KEY (rule_set_id) REFERENCES public.rule_set(rule_set_id);


--
-- Name: rule_set fk_rule_set_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rule_set
    ADD CONSTRAINT fk_rule_set_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: salary_definition fk_salary_definition_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.salary_definition
    ADD CONSTRAINT fk_salary_definition_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: grade grade_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade
    ADD CONSTRAINT grade_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: payroll_reconciliation payroll_reconciliation_payroll_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_reconciliation
    ADD CONSTRAINT payroll_reconciliation_payroll_run_id_fkey FOREIGN KEY (payroll_run_id) REFERENCES public.payroll_run(payroll_run_id);


--
-- Name: payroll_result payroll_result_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_result
    ADD CONSTRAINT payroll_result_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(employee_id);


--
-- Name: payroll_result payroll_result_payroll_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_result
    ADD CONSTRAINT payroll_result_payroll_run_id_fkey FOREIGN KEY (payroll_run_id) REFERENCES public.payroll_run(payroll_run_id);


--
-- Name: payroll_rule payroll_rule_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_rule
    ADD CONSTRAINT payroll_rule_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: payroll_run payroll_run_rule_set_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_run
    ADD CONSTRAINT payroll_run_rule_set_id_fkey FOREIGN KEY (rule_set_id) REFERENCES public.rule_set(rule_set_id);


--
-- Name: payroll_run payroll_run_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_run
    ADD CONSTRAINT payroll_run_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: platform_attendance_code_template platform_attendance_code_template_introduced_in_version_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.platform_attendance_code_template
    ADD CONSTRAINT platform_attendance_code_template_introduced_in_version_fkey FOREIGN KEY (introduced_in_version) REFERENCES public.platform_attendance_template_version(version_tag);


--
-- Name: platform_attendance_policy_template platform_attendance_policy_template_client_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.platform_attendance_policy_template
    ADD CONSTRAINT platform_attendance_policy_template_client_code_fkey FOREIGN KEY (client_code) REFERENCES public.platform_attendance_code_template(client_code);


--
-- Name: platform_attendance_policy_template platform_attendance_policy_template_introduced_in_version_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.platform_attendance_policy_template
    ADD CONSTRAINT platform_attendance_policy_template_introduced_in_version_fkey FOREIGN KEY (introduced_in_version) REFERENCES public.platform_attendance_template_version(version_tag);


--
-- Name: rate_code_registry rate_code_registry_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rate_code_registry
    ADD CONSTRAINT rate_code_registry_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: tax_band tax_band_statutory_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tax_band
    ADD CONSTRAINT tax_band_statutory_rule_id_fkey FOREIGN KEY (statutory_rule_id) REFERENCES public.statutory_rule(statutory_rule_id);


--
-- Name: timesheet_entry timesheet_entry_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timesheet_entry
    ADD CONSTRAINT timesheet_entry_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(employee_id);


--
-- Name: timesheet_entry timesheet_entry_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timesheet_entry
    ADD CONSTRAINT timesheet_entry_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: workspace workspace_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace
    ADD CONSTRAINT workspace_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(account_id);


--
-- Name: workspace workspace_attendance_template_version_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace
    ADD CONSTRAINT workspace_attendance_template_version_fkey FOREIGN KEY (attendance_template_version) REFERENCES public.platform_attendance_template_version(version_tag);


--
-- Name: workspace_payroll_config workspace_payroll_config_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_payroll_config
    ADD CONSTRAINT workspace_payroll_config_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- Name: workspace_public_holiday workspace_public_holiday_workspace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_public_holiday
    ADD CONSTRAINT workspace_public_holiday_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspace(workspace_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 9DK1XYbmRzbWwQDo4FNwPyqdJ8sghjYAVbf7UQ2467Y8FFdOxVh6QjbYcEd89d3

