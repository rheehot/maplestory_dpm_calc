from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobbranch import thieves
from math import ceil
#TODO : 5차 신스킬 적용

######   Passive Skill   ######



class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 11
        self.jobtype = "luk"
        self.jobname = "나이트로드"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1
        self._combat = 0

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('얼티밋 다크 사이트', '스프레드 스로우'), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat

        NimbleBody = core.InformedCharacterModifier("님블 바디",stat_main = 20)
        CriticalThrow = core.InformedCharacterModifier("크리티컬 스로우", crit=50, crit_damage = 5)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        
        Adrenalin = core.InformedCharacterModifier("아드레날린",crit_damage=10)
        JavelinMastery = core.InformedCharacterModifier("자벨린 마스터리",pdamage_indep = 25)    #20%확률로 100%크리. 현재 비활성,
        PurgeAreaPassive = core.InformedCharacterModifier("퍼지 에어리어(패시브)",boss_pdamage = 10 + ceil(self._combat / 3))
        DarkSerenity = core.InformedCharacterModifier("다크 세레니티",att = 40+passive_level, armor_ignore = 30+passive_level)
        
        JavelineExpert = core.InformedCharacterModifier("자벨린 엑스퍼트",att = 30 + passive_level, crit_damage = 15 + passive_level//3)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 1, 1)
        
        return [NimbleBody, CriticalThrow, PhisicalTraining, 
                Adrenalin, JavelinMastery, PurgeAreaPassive, DarkSerenity, JavelineExpert, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat

        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 75)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5+0.5*(passive_level / 2))    #오더스 기본적용!        
        
        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        쿼드-마크-쇼다운
        
        스프 3줄 히트
        
        얼닼사는 스프 사용중에만 사용
        
        '''
        passive_level = chtr.get_base_modifier().passive_level + self._combat
        #Buff skills
        ShadowPartner = core.BuffSkill("쉐도우 파트너", 0, 200 * 1000, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        SpiritJavelin = core.BuffSkill("스피릿 자벨린", 0, 200 * 1000, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        PurgeArea = core.BuffSkill("퍼지 에어리어", 600, (40+self._combat) * 1000, armor_ignore=30+self._combat).wrap(core.BuffSkillWrapper) #딜레이 모름
        BleedingToxin = core.BuffSkill("블리딩 톡신", 780, 90*1000, cooltime = 200 * 1000, att = 60).wrap(core.BuffSkillWrapper)
        BleedingToxinDot = core.DotSkill("블리딩 톡신(도트)", 1000, 90*1000).wrap(core.SummonSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)

        
        QuarupleThrow =core.DamageSkill("쿼드러플 스로우", 600, 378 + 4*self._combat, 5 * 1.7, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)    #쉐도우 파트너 적용
        
        MARK_PROP = (60+2*passive_level)/(160+2*passive_level)
        MarkOfNightlord = core.DamageSkill("마크 오브 나이트로드", 0, (60+3*passive_level+chtr.level), MARK_PROP*3).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        MarkOfNightlordPungma = core.DamageSkill("마크 오브 나이트로드(풍마)", 0, (60+3*passive_level+chtr.level), MARK_PROP*3).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper) # 툴팁대로면 19.355%가 맞으나, 쿼드러플과 동일한 37.5%로 적용되는 중

        # TODO: 타수 분리    
        FatalVenom = core.DotSkill("페이탈 베놈", (160+5*passive_level)*(2+(10+passive_level)//6), 8000).wrap(core.SummonSkillWrapper)
    
        #_VenomBurst = core.DamageSkill("베놈 버스트", ??) ## 패시브 50%확률로 10초간 160+6*vlevel dot. 사용시 도트뎀 모두 피해 + (500+20*vlevel) * 5. 어차피 안쓰는 스킬이므로 작성X
        
        UltimateDarksight = thieves.UltimateDarkSightWrapper(vEhc, 3, 3)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 1, 1)
        
        #조건부 파이널어택으로 설정함.
        SpreadThrowTick = core.DamageSkill("스프레드 스로우(틱)", 0, 378*0.85, 5*3, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        SpreadThrowInit = core.BuffSkill("스프레드 스로우", 540, (30+vEhc.getV(0,0))*1000, cooltime = (240-vEhc.getV(0,0))*1000, red=True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        Pungma = core.SummonSkill("풍마수리검", 360, 100, 250+vEhc.getV(4,4)*10, 5*1.7, 1450, cooltime = 25*1000, red=True).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)   #10타 가정
        ArcaneOfDarklord = core.SummonSkill("다크로드의 비전서", 360, 1020, 350+14*vEhc.getV(2,2), 7 + 5, 11990, cooltime = 60*1000, red=True, modifier=core.CharacterModifier(boss_pdamage=30)).isV(vEhc,2,2).wrap(core.SummonSkillWrapper) # 132타
        ArcaneOfDarklordFinal = core.DamageSkill("다크로드의 비전서(막타)", 0, 900+36*vEhc.getV(2,2), 10, cooltime = -1, modifier=core.CharacterModifier(boss_pdamage=30)).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######

        #조건부 파이널어택으로 설정함.
        SpreadThrow = core.OptionalElement(SpreadThrowInit.is_active, SpreadThrowTick)
        SpreadThrowTick.onAfter(core.RepeatElement(MarkOfNightlord, 15))
        Pungma.onTick(MarkOfNightlordPungma)
        
        ArcaneOfDarklord.onAfter(ArcaneOfDarklordFinal.controller(8000))
        
        BleedingToxin.onAfter(BleedingToxinDot)
        
        QuarupleThrow.onAfters([MarkOfNightlord, SpreadThrow])

        for sk in [QuarupleThrow, Pungma, SpreadThrowTick]:
            sk.onAfter(FatalVenom)

        return (QuarupleThrow, 
            [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    ShadowPartner, SpiritJavelin, PurgeArea, BleedingToxin, EpicAdventure, 
                    UltimateDarksight, ReadyToDie, SpreadThrowInit,
                    globalSkill.soul_contract()] + \
                [ArcaneOfDarklordFinal] + \
                [Pungma, ArcaneOfDarklord, BleedingToxinDot, FatalVenom] +\
                [] + [QuarupleThrow])