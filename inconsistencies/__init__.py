# -*- coding: utf-8 -*-

from . import controllers
from . import models


def _post_init_hook(cr, registry):
    _map_state(cr)
    _translate_state(cr)
    _calculate_inconsistencies(cr)
    _calculate_inconsistent_states(cr)
    _calc_inconsistencies_by_type(cr)
    _calculate_incons_states_by_type(cr)
    return


def _map_state(cr):
    _sql = """
        CREATE or REPLACE FUNCTION mapState(state varchar, value varchar) RETURNS varchar AS $$
        DECLARE 
            result varchar;
        BEGIN
            if state = 'aporto' then
                if value = 'none' then result := 'NACA';
                elsif value = 'baja' then result := 'NACA';
                elsif value = 'hist' then result := 'HCA';
                elsif value = 'pasivo' then result := 'PCA';
                elsif value = 'pend_a' then result := 'PACA';
                elsif value = 'pend_b' then result := 'PBCB';
                elsif value = 'jub' then result := 'JPCA';
                elsif value = 'becarie' then result := 'BPCA';
                elsif value = 'contratade' then result := 'CPCA';
                else result := 'OTRA';
                end if;
            elsif state = 'no_aporto' then
                if value = 'activo' then result := 'ASA';
                elsif value = 'pend_a' then result := 'PASA';
                elsif value = 'pend_b' then result := 'PBSA';
                elsif value = 'juba' then result := 'JASA';
                elsif value = 'becariea' then result := 'BASA';
                elsif value = 'contratadea' then result := 'CASA';
                else result := 'OTRA';
                end if;
            end if;
        RETURN result;
        END; $$
        LANGUAGE PLPGSQL;
    """
    cr.execute(_sql)


def _translate_state(cr):
    _sql = """
        CREATE or REPLACE FUNCTION translateState(state varchar) RETURNS varchar AS $$
        DECLARE 
            result varchar;
        BEGIN
            if state = 'new' then result := 'Nuevo';
            elsif state = 'not_affiliated' then result := 'No afiliado';
            elsif state = 'pending_suscribe' then result := 'Pendiente de alta';
            elsif state = 'pending_unsuscribe' then result := 'Pendiente de baja';
            elsif state = 'disaffiliated' then result := 'Desafiliado';
            else result := 'Historico';
            end if;
        RETURN result;
        END; $$
        LANGUAGE PLPGSQL;
    """
    cr.execute(_sql)


def _calculate_inconsistencies(cr):
    _sql = """
        CREATE or REPLACE FUNCTION calculateInconsistencies(contrib_state varchar, date_from date, date_to date, description varchar)  RETURNS integer AS $$
        DECLARE 
            result integer;
        BEGIN 
            if contrib_state = 'no_aporto' then
                insert into inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description) 
                    select a.id, 'Cotizante sin aportes', date_from, date_to, now(), description  
                    from affiliation_affiliate a  
                    where a.quote=TRUE and a.id not in (
                        select DISTINCT(c.affiliate_id) 
                        from contribution_affiliate_contribution c 
                        where c.date between date_from and date_to 
                        group by c.affiliate_id);
                
                GET DIAGNOSTICS result = ROW_COUNT;
            
            elsif contrib_state = 'aporto' then
                insert into inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description) 
                    select a.id, 'No cotizante con aportes', date_from, date_to, now(), description  
                    from affiliation_affiliate a  
                    where (a.quote=FALSE or a.quote IS NULL) and a.id in (
                        select DISTINCT(c.affiliate_id) 
                        from contribution_affiliate_contribution c 
                        where c.date between date_from and date_to 
                        group by c.affiliate_id);
                            
                GET DIAGNOSTICS result = ROW_COUNT;
            end if;
        RETURN result;
        END; $$
        LANGUAGE PLPGSQL;
    """
    cr.execute(_sql)

def _calculate_inconsistent_states(cr):
    _sql = """
        CREATE or REPLACE FUNCTION calculateInconsistentStates(date_from date, date_to date, description varchar) RETURNS integer AS $$
        DECLARE 
            result integer;
        BEGIN 
            insert into inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description) 
                select a.id, concat('Cotizante',' - ',translateState(a.state)), date_from, date_to, now(), description  
                from affiliation_affiliate a  
                where a.quote=TRUE and a.state != 'affiliated';

            insert into inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description) 
                select a.id, 'No Cotizante - Afiliado', date_from, date_to, now(), description  
                from affiliation_affiliate a  
                where (a.quote=FALSE or a.quote IS NULL) and a.state = 'affiliated';
        RETURN result;
        END; $$
        LANGUAGE PLPGSQL;
    """
    cr.execute(_sql)

def _calc_inconsistencies_by_type(cr):
    _sql = """
        CREATE or REPLACE FUNCTION calcInconsByType(contrib_state varchar, date_from date, date_to date, description varchar, type_id integer)  RETURNS integer AS $$
        DECLARE 
            result integer;
        BEGIN 
            if contrib_state = 'no_aporto' then
                insert into inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description) 
                    select a.id, concat('Cotizante sin aportes (', at.name,')'), date_from, date_to, now(), description  
                    from affiliation_affiliate a  
                    join affiliation_affiliate_type at on(a.affiliate_type_id=at.id) 
                    where a.quote=TRUE and a.affiliate_type_id=type_id and a.id not in (
                        select DISTINCT(c.affiliate_id) 
                        from contribution_affiliate_contribution c 
                        where c.date between date_from and date_to 
                        group by c.affiliate_id);
                
                GET DIAGNOSTICS result = ROW_COUNT;
            
            elsif contrib_state = 'aporto' then
                insert into inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description) 
                    select a.id, concat('No cotizante con aportes (', at.name,')'), date_from, date_to, now(), description  
                    from affiliation_affiliate a  
                    join affiliation_affiliate_type at on(a.affiliate_type_id=at.id) 
                    where (a.quote=FALSE or a.quote IS NULL) and a.affiliate_type_id=type_id and a.id in (
                        select DISTINCT(c.affiliate_id) 
                        from contribution_affiliate_contribution c 
                        where c.date between date_from and date_to 
                        group by c.affiliate_id);
                            
                GET DIAGNOSTICS result = ROW_COUNT;
            end if;
        RETURN result;
        END; $$
        LANGUAGE PLPGSQL;
    """
    cr.execute(_sql)

def _calculate_incons_states_by_type(cr):
    _sql = """
        CREATE or REPLACE FUNCTION calcInconsStateByType(date_from date, date_to date, description varchar, type_id integer)  RETURNS integer AS $$
        DECLARE 
            result integer;
        BEGIN 
            insert into inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description) 
                select a.id, concat('Cotizante',' - ',translateState(a.state)), date_from, date_to, now(), description  
                from affiliation_affiliate a  
                where a.quote=TRUE and a.state != 'affiliated' and a.affiliate_type_id=type_id;

            insert into inconsistencies_result (affiliate_id, status, from_date, to_date, query_date, description) 
                select a.id, 'No Cotizante - Afiliado', date_from, date_to, now(), description  
                from affiliation_affiliate a  
                where (a.quote=FALSE or a.quote IS NULL) and a.state = 'affiliated' and a.affiliate_type_id=type_id;
        RETURN result;
        END; $$
        LANGUAGE PLPGSQL;
    """
    cr.execute(_sql)
