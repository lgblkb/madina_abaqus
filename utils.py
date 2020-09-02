from typing import List


class Keyword(object):
    def __init__(self, keyword_name, **params):
        self.keyword_name = keyword_name
        self.params = params
        self.data = list()

    @classmethod
    def from_line(cls, line):
        keyword_info = process_keyword(line)
        return cls(keyword_info['name'], **keyword_info['params'])

    def __bool__(self):
        return True

    def __eq__(self, other):
        if isinstance(other, str):
            return self.keyword_name == other
        elif isinstance(other, Keyword):
            return self.keyword_name == other.keyword_name

    def read_data_as_list(self, line):
        parts = line.replace(' ', '').split(',')
        self.data.append(parts)

    def get_lines(self):
        out_params = list()
        for k, v in self.params.items():
            if isinstance(v, bool) and v:
                out_params.append(k)
            else:
                out_params.append(f"{k}={v}")
        lines = list()
        lines.append("*" + ", ".join(map(str, [self.keyword_name] + out_params)))
        lines.extend([", ".join(map(str, line_data)) for line_data in self.data])
        return lines


class Step(object):
    def __init__(self, keywords):
        self.keywords: List[Keyword] = keywords

    @staticmethod
    def from_template(template_file):
        step = get_steps(template_file)[0]
        return step

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.keywords[item]
        elif isinstance(item, str):
            for keyword in self.keywords:
                if keyword.keyword_name == item:
                    return keyword
        else:
            raise NotImplementedError('Unsupported type of index', dict(item_type=str(type(item))))

    def __len__(self):
        return len(self.keywords)

    def get_lines(self):
        last_line = "** ----------------------------------------------------------------"
        # return "\n".join([x.render() for x in self.keywords] + [last_line])
        lines = list()
        for keyword in self.keywords:
            lines.extend(keyword.get_lines())
        return lines + [last_line]


def process_keyword(line):
    # logger.info("line: %s",line)
    keyword_info = dict()
    parts = [x.strip() for x in line.split(',')]
    keyword_info['name'] = parts[0][1:]
    keyword_params = dict()
    for key_value_pair in parts[1:]:
        if '=' in key_value_pair:
            key, value = key_value_pair.split('=')
            keyword_params[key] = value
        else:
            keyword_params[key_value_pair] = True
    keyword_info['params'] = keyword_params
    return keyword_info


def get_keywords(keywords_filepath):
    with open(keywords_filepath) as file:
        lines = file.readlines()

    keywords = list()
    current_keyword = None
    for i, line in enumerate(lines):
        line = line.strip()  # remove trailing spaces and newline characters
        # logger.debug("line: %s", line)
        if line.startswith('**'):  # I suppose double star represents a commented line?
            continue
        elif line.startswith('*'):  # Keyword line. Contains name of the keyword and optionally some parameters
            current_keyword = Keyword.from_line(line)
            keywords.append(current_keyword)
        elif current_keyword:
            current_keyword.read_data_as_list(line)
    return keywords


def get_steps(steps_filepath):
    with open(steps_filepath) as file:
        lines = file.readlines()

    steps = list()
    step_keywords = list()
    current_keyword = None
    for i, line in enumerate(lines):
        line = line.strip()  # remove trailing spaces and newline characters
        # logger.debug("line: %s", line)
        if line.startswith('**'):  # I suppose double star represents a commented line?
            continue
        elif line.startswith('*'):  # Keyword line. Contains name of the keyword and optionally some parameters

            current_keyword = Keyword.from_line(line)
            step_keywords.append(current_keyword)
            if current_keyword.keyword_name == 'End Step':
                steps.append(Step(step_keywords.copy()))
                step_keywords.clear()
        elif current_keyword:
            current_keyword.read_data_as_list(line)
    return steps


def write_steps(steps, out_filepath, mode='w'):
    with open(out_filepath, mode) as file:
        for step in steps:
            file.write("\n".join(step.get_lines()))
            file.write("\n")
