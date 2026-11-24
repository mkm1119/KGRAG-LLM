#!/usr/bin/env python3
"""소결을 모두 빼고 장의 끝에 '최종 산출물'을 하나씩 둔다(한 번만 실행, 이전 내용은 sections/_old8).
사용: python3 dam_pilot_data/scripts/apply_outputs_1124.py
"""
import glob, json, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.join(HERE, '..', '..', 'project_khnp', 'final_report', 'sections')
OLD = os.path.join(SEC, '_old8')
assert not os.path.exists(OLD), '이미 실행함'
os.makedirs(OLD)
for p in sorted(glob.glob(os.path.join(SEC, '*.json'))):
    shutil.copy(p, OLD)
    L = json.load(open(p, encoding='utf-8'))
    out, skip = [], False
    for k, v in L:
        if k in ('H3', 'H4'):
            skip = v.endswith('소결')
        if not skip:
            out.append([k, v])
    if len(out) != len(L):
        print(os.path.basename(p), '소결 삭제', len(L) - len(out), '항목')
        json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def outputs(label, rows):
    return [['BODY', '세부 항목별 최종 산출물은 ⟦표:%s⟧와 같다.' % label],
            ['TABLE', {'label': label, 'caption': '최종 산출물', 'widths': [28, 72], 'align': ['l', 'l'], 'rows': [['세부 항목', '산출물']] + rows}]]


F = {'1_4': outputs('s1_out', [
        ['수자원 분야 사례 조사', '유형별 사례 목록과 항목 비교표, 주요 사례의 구성과 결과\n세 유형의 특성(⟦표:type_compare⟧)\n댐 운영 의사결정 지원에 적합한 구성(⟦표:s115_fit⟧)'],
        ['국내 운영 여건 조사', '착수보고회에서 제시된 운영 여건의 주요 쟁점\n기술 적용 시 고려사항\n【현장방문 후 작성】 현장방문 조사 결과'],
        ['적용 기술요소 및 모델 제안', '조사 결과에서 도출한 다섯 기술요소(⟦표:s13_derive⟧)와 기술요소별로 검토한 방식의 비교표\n파트별 적용 기술(안)과 후속 검토 사항(⟦표:s13_summary⟧)\n지식기반·검색·응답의 3계층으로 이루어진 RAG-sLLM 아키텍처(안)']]),
     '2_4': outputs('s2_out', [
        ['수집 경로 조사', '수문, 기상, 방류 승인 기록, 운영 규정의 수집 경로 비교표와 자료별 데이터 형태\n자료별 적정 수집 경로(안)(⟦표:s21_route⟧)\n한수원 내부 센서 및 운영 자료의 조사 항목'],
        ['온톨로지·메타데이터 설계방안 조사', '메타데이터 설계요소(안): 식별 키, 출처·시점 정보, 단위와 표기 형식, 자료 유형\n자료 유형별 전처리 체계(안)와 공통 정리 항목(안)\n댐 운영 온톨로지 설계(안): Class 6개와 관계 6종, 외부 저장소와의 연계 구조\n온톨로지 설계·보완 절차(안)'],
        ['RAG-LLM 통합 파이프라인(안) 제시', '7단계 RAG-LLM 통합 파이프라인(안)과 단계별 입력·처리·산출(⟦표:s23_stage⟧)\n표준 프롬프트 프레임(안)\n근거 사용 원칙(안)(⟦표:s23_principle⟧)']])}
for f, items in F.items():
    json.dump(items, open(os.path.join(SEC, f + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
