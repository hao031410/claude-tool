package io.terminus.tsrm.partner.spi.convert.grade;

import io.terminus.tsrm.partner.spi.model.grade.po.GradeRulePO;
import io.terminus.tsrm.partner.spi.model.grade.dto.GradeRuleDTO;
import org.mapstruct.Mapper;

import java.util.List;

/**
 * 等级规则表(GradeRule)结构映射器
 *
 * @author system
 * @since 2024-01-06 10:00:00
 */
@Mapper(componentModel = "spring")
public interface GradeRuleConverter {

    GradeRuleDTO po2Dto(GradeRulePO po);

    List<GradeRuleDTO> po2DtoList(List<GradeRulePO> poList);

    GradeRulePO dto2Po(GradeRuleDTO dto);

    List<GradeRulePO> dto2PoList(List<GradeRuleDTO> dtoList);
}