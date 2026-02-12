package io.terminus.tsrm.partner.infrastructure.repo.grade;

import io.terminus.common.mybatis.repository.BaseRepository;
import io.terminus.tsrm.partner.spi.model.grade.po.GradeRulePO;
import org.springframework.stereotype.Repository;

/**
 * 等级规则表(GradeRule)表数据库访问层
 *
 * @author system
 * @since 2024-01-06 10:00:00
 */
@Repository
public interface GradeRuleRepo extends BaseRepository<GradeRulePO> {
}