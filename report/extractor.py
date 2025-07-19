"""Data extractor for extracting specific data from parsed XML.

这个模块提供了专门的数据提取器，用于从解析后的XML报告文件中提取特定的数据字段。
支持提取多种类型的数据，包括用户信息、脑疲劳数据、心理生理状态和心态分布等。

主要功能：
- 用户基本信息提取（姓名、UUID、年龄等）
- 脑疲劳状态和程度提取
- 心理生理状态各项因子提取
- 心态分布曲线数据提取
- 完整的数据验证和错误处理

支持的数据类型：
- UserInfo: 用户基本信息
- BrainFatigue: 脑疲劳相关数据
- Psycho-physiologicalState: 心理生理状态
- MindDistribution: 心态分布和曲线数据

使用示例：
    extractor = DataExtractor(xml_root)
    user_info = extractor.extract_user_info()
    all_data = extractor.extract_all_data()
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List, Union


class DataExtractor:
    """XML报告数据提取器。
    
    这个类负责从解析后的XML根元素中提取各种类型的数据。
    提供了多个专门的方法来提取不同类别的信息，确保数据的完整性和准确性。
    
    Attributes:
        root (ET.Element): XML文档的根元素，包含所有待提取的数据
    
    Note:
        - 所有提取方法都包含错误处理，确保在数据缺失时返回合理的默认值
        - 支持中文字段名称的识别和处理
        - 提供了灵活的数据格式适配能力
    """
    
    def __init__(self, root: ET.Element) -> None:
        """初始化数据提取器。
        
        Args:
            root (ET.Element): 解析后的XML根元素
            
        Raises:
            TypeError: 当root不是ET.Element类型时抛出
        """
        if not isinstance(root, ET.Element):
            raise TypeError("root must be an ET.Element instance")
        self.root = root
    
    def extract_user_info(self) -> Dict[str, Any]:
        """提取用户基本信息。
        
        从XML的UserInfo节点中提取用户的基本信息，包括UUID、姓名、性别、
        年龄、公司、地点和日期等字段。
        
        Returns:
            Dict[str, Any]: 包含用户信息的字典，键为字段名，值为对应的数据
            
        Note:
            - 如果某个字段不存在，会返回空字符串作为默认值
            - 支持的字段：uuid, name, gender, age, company, site, date
            - 所有字段值都会被转换为字符串类型
        """
        user_info = {}
        user_info_elem = self.root.find('UserInfo')
        
        if user_info_elem is not None:
            user_info['uuid'] = self._get_text(user_info_elem, 'uuid')
            user_info['name'] = self._get_text(user_info_elem, 'name')
            user_info['gender'] = self._get_text(user_info_elem, 'gender')
            user_info['age'] = self._get_text(user_info_elem, 'age')
            user_info['company'] = self._get_text(user_info_elem, 'company')
            user_info['site'] = self._get_text(user_info_elem, 'site')
            user_info['date'] = self._get_text(user_info_elem, 'date')
        
        return user_info
    
    def extract_brain_fatigue(self) -> Dict[str, Any]:
        """提取脑疲劳相关数据。
        
        从XML的BrainFatigue节点中提取脑疲劳状态、程度、情绪和能量等信息。
        这些数据反映了用户的认知负荷和精神状态。
        
        Returns:
            Dict[str, Any]: 包含脑疲劳信息的字典
            
        提取的字段：
            - brain_fatigue_state: 脑疲劳状态
            - brain_fatigue_level: 脑疲劳度
            - emotion: 情绪状态
            - energy: 能量水平
            
        Note:
            - 通过title属性匹配对应的中文字段名
            - 如果节点不存在，对应字段将不会出现在返回字典中
        """
        brain_fatigue = {}
        brain_fatigue_elem = self.root.find('BrainFatigue')
        
        if brain_fatigue_elem is not None:
            # Extract State (脑疲劳状态)
            state_elem = brain_fatigue_elem.find('State[@title="脑疲劳状态"]')
            if state_elem is not None:
                brain_fatigue['brain_fatigue_state'] = state_elem.text
            
            # Extract Level (脑疲劳度)
            level_elem = brain_fatigue_elem.find('Level[@title="脑疲劳度"]')
            if level_elem is not None:
                brain_fatigue['brain_fatigue_level'] = level_elem.text
            
            # Extract Information (情绪)
            info_elem = brain_fatigue_elem.find('Information[@title="情绪"]')
            if info_elem is not None:
                brain_fatigue['emotion'] = info_elem.text
            
            # Extract Energy (能量)
            energy_elem = brain_fatigue_elem.find('Energy[@title="能量"]')
            if energy_elem is not None:
                brain_fatigue['energy'] = energy_elem.text
        
        return brain_fatigue
    
    def extract_psycho_physiological_state(self) -> Dict[str, Any]:
        """提取心理生理状态数据。
        
        从XML的Psycho-physiologicalState节点中提取情绪变化和各项心理因子的数据。
        包括情绪变化信息和多个心理因子的统计数据（平均值、最大值、最小值等）。
        
        Returns:
            Dict[str, Any]: 包含心理生理状态信息的字典
            
        提取的数据类型：
            1. 情绪变化 (EmotionalVariation):
               - emotional_variation_title: 标题
               - emotional_variation_decision: 判断结果
               - emotional_variation_value: 数值
               - emotional_variation_text: 文本内容
               
            2. 心理因子 (Factor):
               对每个因子提取以下统计数据：
               - {因子名}_range_min: 范围最小值
               - {因子名}_range_max: 范围最大值
               - {因子名}_min: 最小值
               - {因子名}_average: 平均值
               - {因子名}_max: 最大值
               - {因子名}_judge: 判断结果
               
        Note:
            - 支持的心理因子包括：攻击性、压力、不安、怀疑、平衡、自信、能量等
            - 所有数值都保持原始字符串格式，便于后续处理
        """
        psycho_state = {}
        psycho_elem = self.root.find('Psycho-physiologicalState')
        
        if psycho_elem is not None:
            # Extract emotional variation
            emotion_elem = psycho_elem.find('EmotionalVariation')
            if emotion_elem is not None:
                psycho_state['emotional_variation_title'] = emotion_elem.get('title', '')
                psycho_state['emotional_variation_decision'] = emotion_elem.get('decision', '')
                psycho_state['emotional_variation_value'] = emotion_elem.get('value', '')
                psycho_state['emotional_variation_text'] = emotion_elem.text
            
            # Extract factor items
            factor_elem = psycho_elem.find('Factor')
            if factor_elem is not None:
                factors = {}
                for item in factor_elem.findall('item'):
                    title = item.get('title', '')
                    if title:
                        factors[f'{title}_range_min'] = self._get_text(item, 'range_min')
                        factors[f'{title}_range_max'] = self._get_text(item, 'range_max')
                        factors[f'{title}_min'] = self._get_text(item, 'min')
                        factors[f'{title}_average'] = self._get_text(item, 'average')
                        factors[f'{title}_max'] = self._get_text(item, 'max')
                        factors[f'{title}_judge'] = self._get_text(item, 'judge')
                
                psycho_state.update(factors)
        
        return psycho_state
    
    def extract_mind_distribution(self) -> Dict[str, Any]:
        """提取心态分布数据。
        
        从XML的MindDistribution节点中提取心态分布的基本信息和曲线数据摘要。
        包括分布标题、曲线标题和样本数据点等。
        
        Returns:
            Dict[str, Any]: 包含心态分布信息的字典
            
        提取的字段：
            - mind_distribution_title: 心态分布标题
            - distribution_curve_title: 分布曲线标题
            - distribution_points_count: 数据点总数
            - sample_distribution_points: 前5个数据点的样本（格式：(x, y)）
            
        Note:
            - 只提取前5个数据点作为样本，完整数据请使用extract_distribution_curve_data方法
            - 数据点格式为坐标对：(x值, y值)
            - 如果没有找到曲线数据，相关字段将不会出现在返回字典中
        """
        mind_dist = {}
        mind_elem = self.root.find('MindDistribution')
        
        if mind_elem is not None:
            mind_dist['mind_distribution_title'] = mind_elem.get('title', '')
            
            # Extract distribution curve points
            curve_elem = mind_elem.find('DistributionCurve')
            if curve_elem is not None:
                mind_dist['distribution_curve_title'] = curve_elem.get('title', '')
                
                # Extract sample points (first 10 for summary)
                points = curve_elem.findall('pt')
                if points:
                    mind_dist['distribution_points_count'] = len(points)
                    # Store first few points as sample
                    sample_points = []
                    for i, pt in enumerate(points[:5]):  # First 5 points as sample
                        x_val = pt.get('x', '')
                        y_val = pt.get('y', '')
                        sample_points.append(f'({x_val}, {y_val})')
                    mind_dist['sample_distribution_points'] = '; '.join(sample_points)
        
        return mind_dist
    
    def extract_distribution_curve_data(self) -> List[Dict[str, str]]:
        """提取完整的心态分布曲线数据。
        
        从XML的MindDistribution/DistributionCurve节点中提取所有的曲线数据点，
        包括每个点的ID和坐标信息。这个方法用于获取完整的曲线数据用于分析和可视化。
        
        Returns:
            List[Dict[str, str]]: 包含所有曲线点的列表，每个点包含以下字段：
                - point_id: 点的标识符（如pt0, pt1, pt2等）
                - x: X坐标值（字符串格式）
                - y: Y坐标值（字符串格式）
                
        Note:
            - 返回所有找到的数据点，通常包含数百个点
            - 坐标值保持原始字符串格式，便于精确处理
            - 点的标识符按照XML中的顺序排列
            - 如果没有找到曲线数据，返回空列表
        """
        curve_data = []
        mind_elem = self.root.find('MindDistribution')
        
        if mind_elem is not None:
            curve_elem = mind_elem.find('DistributionCurve')
            if curve_elem is not None:
                # Find all point elements (pt0, pt1, pt2, etc.)
                for child in curve_elem:
                    if child.tag.startswith('pt'):
                        point_data = {
                            'point_id': child.tag,
                            'x': child.get('x', ''),
                            'y': child.get('y', '')
                        }
                        curve_data.append(point_data)
        
        return curve_data
    
    def extract_base_curve_data(self) -> List[Dict[str, str]]:
        """提取基准曲线数据。
        
        从XML的MindDistribution/BaseCurve节点中提取标准正态分布曲线的数据点，
        用于与心态分布曲线进行对比分析。
        
        Returns:
            List[Dict[str, str]]: 包含所有基准曲线点的列表，每个点包含以下字段：
                - point_id: 点的标识符（如pt0, pt1, pt2等）
                - x: X坐标值（字符串格式）
                - y: Y坐标值（字符串格式）
                
        Note:
            - 基准曲线通常是标准正态分布
            - 用于与实际心态分布曲线进行对比
            - 如果没有找到基准曲线数据，返回空列表
        """
        base_curve_data = []
        mind_elem = self.root.find('MindDistribution')
        
        if mind_elem is not None:
            base_curve_elem = mind_elem.find('BaseCurve')
            if base_curve_elem is not None:
                # Find all point elements (pt0, pt1, pt2, etc.)
                for child in base_curve_elem:
                    if child.tag.startswith('pt'):
                        point_data = {
                            'point_id': child.tag,
                            'x': child.get('x', ''),
                            'y': child.get('y', '')
                        }
                        base_curve_data.append(point_data)
        
        return base_curve_data
    
    def extract_all_data(self) -> Dict[str, Any]:
        """提取所有数据字段。
        
        这是一个便捷方法，会调用所有其他提取方法来获取完整的数据集。
        适用于需要获取XML文件中所有可用数据的场景。
        
        Returns:
            Dict[str, Any]: 包含所有提取数据的综合字典，合并了以下数据：
                - 用户基本信息
                - 脑疲劳数据
                - 心理生理状态数据
                - 心态分布数据
                
        Note:
            - 如果某个数据类型的提取失败，不会影响其他数据的提取
            - 返回的字典包含所有成功提取的字段
            - 字段名不会重复，每个数据类型使用不同的前缀
        """
        all_data = {}
        
        # Extract all data sections
        all_data.update(self.extract_user_info())
        all_data.update(self.extract_brain_fatigue())
        all_data.update(self.extract_psycho_physiological_state())
        all_data.update(self.extract_mind_distribution())
        
        return all_data
    
    def _get_text(self, parent: ET.Element, tag: str) -> str:
        """获取子元素的文本内容。
        
        这是一个私有辅助方法，用于安全地从父元素中获取指定标签的文本内容。
        提供了错误处理，确保在元素不存在时返回合理的默认值。
        
        Args:
            parent (ET.Element): 父元素
            tag (str): 要查找的子元素标签名
            
        Returns:
            str: 子元素的文本内容，如果元素不存在或文本为空则返回空字符串
            
        Note:
            - 自动处理None值和空文本的情况
            - 确保返回值始终为字符串类型
            - 用于统一的文本提取逻辑
        """
        elem = parent.find(tag)
        return elem.text if elem is not None and elem.text else ''