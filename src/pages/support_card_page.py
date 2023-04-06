from src.pages.common_page import *

_rarity_name_mapping = {
    SupportCardRarity.R: "R",
    SupportCardRarity.SR: "SR",
    SupportCardRarity.SSR: "SSR",
}
_card_type_name_mapping = {
    SupportCardType.Speed: "速度",
    SupportCardType.Stamina: "耐力",
    SupportCardType.Power: "力量",
    SupportCardType.Guts: "根性",
    SupportCardType.Wiz: "智力",
    SupportCardType.Friend: "友情",
    SupportCardType.Team: "团队",
}


class SupportCardDatabasePage(DatabasePage):

    def createPropertiesForPage(support_card_id, support_card_name, support_card_rarity: SupportCardRarity, support_card_type: SupportCardType):
        return {
            "支援卡名称": Property(title=[RichText(text=Text(support_card_name))]),
            "支援卡稀有度": Property(select=SelectOptions(name=_rarity_name_mapping[support_card_rarity])),
            "支援卡类型": Property(select=SelectOptions(name=_card_type_name_mapping[support_card_type])),
            "id": Property(rich_text=[RichText(text=Text(content=support_card_id))]),
        }

    def __init__(self) -> None:
        super().__init__()
        self._properties = {
            "支援卡名称": Property(title={}),
            "支援卡稀有度": Property(select=PropertySelect(options=[
                SelectOptions(
                    name=_rarity_name_mapping[SupportCardRarity.R], color=ColorType.gray),
                SelectOptions(
                    name=_rarity_name_mapping[SupportCardRarity.SR], color=ColorType.yellow),
                SelectOptions(
                    name=_rarity_name_mapping[SupportCardRarity.SSR], color=ColorType.purple),
            ])),
            "支援卡类型": Property(select=PropertySelect(options=[
                SelectOptions(
                    name=_card_type_name_mapping[SupportCardType.Speed], color=ColorType.blue),
                SelectOptions(
                    name=_card_type_name_mapping[SupportCardType.Stamina], color=ColorType.red),
                SelectOptions(
                    name=_card_type_name_mapping[SupportCardType.Power], color=ColorType.orange),
                SelectOptions(
                    name=_card_type_name_mapping[SupportCardType.Guts], color=ColorType.pink),
                SelectOptions(
                    name=_card_type_name_mapping[SupportCardType.Wiz], color=ColorType.green),
                SelectOptions(
                    name=_card_type_name_mapping[SupportCardType.Friend], color=ColorType.brown),
                SelectOptions(
                    name=_card_type_name_mapping[SupportCardType.Team], color=ColorType.purple),
            ])),
            "id": Property(rich_text={}),
        }

    def createDatabase(self, database_name, parent_page_id: str) -> Database:
        return createDatabase(CreateDatabaseRequest(
            parent=Parent(type=ParentType.PAGE, page_id=parent_page_id),
            title=[RichText(text=Text(content=database_name))],
            properties=self._properties
        ))
    
    def filterNewCard(self, card_list: list[SupportCard], database_id: str) -> list[SupportCard]:
        id_set = self.getIdSetInNotionDatabase(database_id)
        return list(filter(lambda card: card.id not in id_set, card_list))


class SupportCardDetailPage:

    def __init__(self, cover_mapping=None, icon_mapping=None) -> None:
        self.failed_count = 0
        self.cover_mapping = cover_mapping
        self.icon_mapping = icon_mapping

    def createPageInDatabase(self, database_id, card: SupportCard, skill_page_mapping: StrMapping, mismatch: Callable[[str], str]):
        icon_file = None
        if self.icon_mapping is not None:
            icon_file = File(
                type=FileType.external,
                external=ExternalFile(url=self.icon_mapping.get(card.id))
            )
            if not icon_file.external.url:
                icon_file = None
                print(f"Icon for {card.name}:({card.id}) not found.")
        cover_file = None
        if self.cover_mapping is not None:
            cover_file = File(
                type=FileType.external,
                external=ExternalFile(url=self.cover_mapping.get(card.id))
            )
            if not cover_file.external.url:
                cover_file = None
                print(f"Cover for {card.name}:({card.id}) not found.")
        try:
            children_list = self._createPageDetail(
                card, skill_page_mapping, mismatch)
            createPage(CreatePageRequest(
                parent=Parent(type=ParentType.DATABASE,
                              database_id=database_id),
                properties=SupportCardDatabasePage.createPropertiesForPage(
                    card.id, card.name, card.rarity, card.type),
                children=children_list,
                icon=icon_file,
                cover=cover_file,
            ))
        except Exception as e:
            traceback.print_exc()
            self.failed_count += 1

    def _getSkillPageId(self, skill_id: int, skill_page_mapping: StrMapping, mismatch: Callable[[str], str]) -> str:
        if skill_id in skill_page_mapping:
            return skill_page_mapping[skill_id]
        return mismatch(skill_id)

    def _createPageDetail(self, card: SupportCard, skill_page_mapping, mismatch) -> list[Block]:
        block_list = []
        if card.original_name:
            block_list.append(Block(heading_2=Heading2(
                rich_text=[RichText(text=Text(content="描述信息"))])))
            block_list.append(Block(
                paragraph=Paragraph(rich_text=[
                    RichText(text=Text(content="技能原名："), annotations=Annotation(
                        bold=True, color=ColorType.purple)),
                    RichText(text=Text(content=card.original_name)),
                ])
            ))
        block_list.extend(self._createEventSkillList(card, skill_page_mapping, mismatch))
        block_list.extend(self._createTrainSkillList(card, skill_page_mapping, mismatch))
        block_list.extend(self._createEffectTable(card))
        return block_list

    def _createEventSkillList(self, card: SupportCard, skill_page_mapping, mismatch) -> list[Block]:
        ret = [Block(heading_2=Heading2(
            rich_text=[RichText(text=Text(content="事件取得技能"))]))]
        if card.event_skill_list:
            for skill_id in card.event_skill_list:
                page_id = self._getSkillPageId(
                    skill_id, skill_page_mapping, mismatch)
                if page_id:
                    ret.append(Block(paragraph=Paragraph(rich_text=[
                        RichText(type=RichTextType.mention, mention=Mention(type=MentionType.page, page=MentionPage(id=page_id)))])))
        ret.append(Block(divider={}))
        return ret

    def _createTrainSkillList(self, card: SupportCard, skill_page_mapping, mismatch) -> list[Block]:
        ret = [Block(heading_2=Heading2(
            rich_text=[RichText(text=Text(content="训练取得技能"))]))]
        if card.train_skill_list:
            for skill_id in card.train_skill_list:
                page_id = self._getSkillPageId(
                    skill_id, skill_page_mapping, mismatch)
                if page_id:
                    ret.append(Block(paragraph=Paragraph(rich_text=[
                        RichText(type=RichTextType.mention, mention=Mention(type=MentionType.page, page=MentionPage(id=page_id))), 
                        RichText(text=Text(content="  "))])))
        ret.append(Block(divider={}))
        return ret
    
    def _createEffectTable(self, card: SupportCard) -> list[Block]:
        ret = [Block(heading_2=Heading2(
            rich_text=[RichText(text=Text(content="基础效果信息"))]))]
        if card.unique_effect:
            # appedn unique effect block
            pass
        if card.effect_table_set:
            # append common effect block
            pass
        return ret
        